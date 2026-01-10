#config/base_config.py
import json
from dataclasses import dataclass, field, asdict, is_dataclass
from typing import List, Dict, Any, Optional, Union, Callable, get_type_hints, get_origin, get_args
from enum import Enum
import inspect
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Import enums
from .enums import AlgorithmType, HeuristicType, StackType, StackGenerationStrategy

class ConfigJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for configuration objects"""
    def default(self, obj):
        if isinstance(obj, Enum):
            return {"__enum__": True, "class": obj.__class__.__name__, "value": obj.value}
        elif is_dataclass(obj) and hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif callable(obj):
            # Don't serialize functions
            return None
        return super().default(obj)

class ConfigJSONDecoder(json.JSONDecoder):
    """Custom JSON decoder for configuration objects"""
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, dct):
        if "__enum__" in dct:
            # Import enum classes dynamically
            from .enums import AlgorithmType, HeuristicType, StackType, StackGenerationStrategy
            enum_classes = {
                "AlgorithmType": AlgorithmType,
                "HeuristicType": HeuristicType,
                "StackType": StackType,
                "StackGenerationStrategy": StackGenerationStrategy
            }
            enum_class = enum_classes.get(dct["class"])
            if enum_class:
                for member in enum_class:
                    if member.value == dct["value"]:
                        return member
        elif "__datetime__" in dct:
            return datetime.fromisoformat(dct["value"])
        return dct


@dataclass
class BaseConfig:
    """Base configuration class with serialization methods"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        for key, value in asdict(self).items():
            if callable(value):
                # Skip functions
                continue
            elif isinstance(value, datetime):  # Handle datetime
                result[key] = value.isoformat()
            elif is_dataclass(value):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if is_dataclass(item) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                result[key] = {
                    k: v.to_dict() if is_dataclass(v) else v
                    for k, v in value.items()
                }
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    def to_json(self, filepath: Optional[str] = None) -> str:
        """Serialize to JSON using custom encoder"""
        json_str = json.dumps(self.to_dict(), cls=ConfigJSONEncoder, indent=2)
    
        if filepath:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            Path(filepath).write_text(json_str)
    
        return json_str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseConfig':
        """Create config from dictionary with type conversion"""
        # Get type hints for the class
        type_hints = get_type_hints(cls)
        
        # Process each field
        processed_data = {}
        for field_name, field_type in type_hints.items():
            if field_name in data:
                value = data[field_name]
                
                # Handle Optional types
                origin = get_origin(field_type)
                if origin is Union:
                    # Get the non-None type
                    args = get_args(field_type)
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if len(non_none_args) == 1:
                        field_type = non_none_args[0]
                        origin = get_origin(field_type)
                
                # Convert based on type
                processed_data[field_name] = cls._convert_value(value, field_type, field_name)
        
        return cls(**processed_data)
    
    @classmethod
    def _convert_value(cls, value: Any, target_type: Any, field_name: str = "") -> Any:
        """Convert value to target type with special handling for our config classes"""
        
        # Handle None values
        if value is None:
            return None
        
        # Handle datetime
        if target_type is datetime:
            if isinstance(value, str):
                return datetime.fromisoformat(value)
            elif isinstance(value, datetime):
                return value
            else:
                raise TypeError(f"Cannot convert {type(value)} to datetime")
        
        # Handle enums
        if inspect.isclass(target_type) and issubclass(target_type, Enum):
            if isinstance(value, str):
                # Try to get enum by value
                try:
                    return target_type(value)
                except ValueError:
                    # Try to get enum by name
                    try:
                        return target_type[value]
                    except KeyError:
                        raise ValueError(f"Cannot convert {value} to {target_type}")
            elif isinstance(value, target_type):
                return value
            else:
                raise TypeError(f"Cannot convert {type(value)} to {target_type}")
        
        # Handle dataclasses (our config classes)
        if inspect.isclass(target_type) and is_dataclass(target_type) and issubclass(target_type, BaseConfig):
            if isinstance(value, dict):
                return target_type.from_dict(value)
            elif isinstance(value, target_type):
                return value
            else:
                raise TypeError(f"Expected dict or {target_type} for {field_name}, got {type(value)}")
        
        # Handle lists of dataclasses
        origin = get_origin(target_type)
        if origin is list or origin == list:
            args = get_args(target_type)
            if args and len(args) == 1:
                item_type = args[0]
                if inspect.isclass(item_type) and is_dataclass(item_type) and issubclass(item_type, BaseConfig):
                    if isinstance(value, list):
                        return [
                            item_type.from_dict(item) if isinstance(item, dict) else item
                            for item in value
                        ]
        
        # Handle dicts of dataclasses
        if origin is dict or origin == dict:
            args = get_args(target_type)
            if args and len(args) == 2:
                key_type, value_type = args
                if inspect.isclass(value_type) and is_dataclass(value_type) and issubclass(value_type, BaseConfig):
                    if isinstance(value, dict):
                        return {
                            key: value_type.from_dict(val) if isinstance(val, dict) else val
                            for key, val in value.items()
                        }
        
        # Default: return as-is (will be validated by dataclass)
        return value
    
    @classmethod
    def from_json(cls, filepath: str) -> 'BaseConfig':
        """Load config from JSON file using custom decoder"""
        with open(filepath, 'r') as f:
            data = json.load(f, cls=ConfigJSONDecoder)
        return cls.from_dict(data)
    
    def validate(self) -> List[str]:
        """Validate configuration, return list of errors"""
        errors = []
        
        # Basic validation for all fields
        for field_name, field_value in asdict(self).items():
            if field_value is None:
                errors.append(f"Field '{field_name}' cannot be None")
        
        return errors
    
    def merge(self, other: 'BaseConfig') -> 'BaseConfig':
        """Merge another config into this one (other takes precedence)"""
        self_dict = self.to_dict()
        other_dict = other.to_dict()
        
        # Deep merge dictionaries
        merged = self._deep_merge(self_dict, other_dict)
        
        return self.__class__.from_dict(merged)
    
    def _deep_merge(self, dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
