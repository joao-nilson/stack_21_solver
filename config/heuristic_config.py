# config/heuristic_config.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
from .base_config import BaseConfig
from .enums import HeuristicType


@dataclass
class HeuristicConfig(BaseConfig):
    """Configuration for a heuristic evaluation function"""
    
    # Basic properties - name MUST come before heuristic_type for from_dict
    name: str
    heuristic_type: HeuristicType
    description: str = ""
    
    # Function to call (can be None if using built-in) - will not be serialized
    evaluation_function: Optional[Callable] = None
    
    # Parameters for the heuristic - use simple dict
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Weight configuration for composite heuristics
    weights: Dict[str, float] = field(default_factory=dict)
    
    # Normalization settings
    normalize_output: bool = True
    output_range: Tuple[float, float] = (-1000, 1000)
    
    def __post_init__(self):
        """Initialize default parameters based on heuristic type"""
        # Call parent __post_init__ if it exists
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        
        # Initialize empty dicts if None
        if self.parameters is None:
            self.parameters = {}
        if self.weights is None:
            self.weights = {}
        
        # Set default parameters if not set and not custom heuristic
        if not self.parameters and self.heuristic_type != HeuristicType.CUSTOM:
            self._set_default_parameters()
        
        # Set default weights for balanced heuristic
        if not self.weights and self.heuristic_type == HeuristicType.BALANCED:
            self.weights = {
                "closeness": 0.4,
                "safety": 0.3,
                "aggression": 0.2,
                "flexibility": 0.1
            }

    def _set_default_parameters(self):
        """Set default parameters for built-in heuristics"""
        if self.heuristic_type == HeuristicType.CLOSENESS:
            self.parameters = {
                "distance_weight": 50,
                "bust_penalty": 10000,
                "win_bonus": 10000
            }
        elif self.heuristic_type == HeuristicType.AGGRESSIVE:
            self.parameters = {
                "total_weight": 100,
                "close_bonus": 500,
                "bust_penalty": 50000
            }
        elif self.heuristic_type == HeuristicType.CAUTIOUS:
            self.parameters = {
                "safety_margin": 4,
                "safe_bonus": 1000,
                "danger_penalty": 1000,
                "bust_penalty": 50000
            }
        elif self.heuristic_type == HeuristicType.BALANCED:
            self.parameters = {
                "distance_weight": 20,
                "stack_consideration": 5,
                "flexibility_bonus": 10
            }
    
    def get_heuristic_key(self) -> str:
        """Get unique key for this heuristic configuration"""
        params_key = "_".join(f"{k}_{v}" for k, v in sorted(self.parameters.items()))
        weights_key = "_".join(f"{k}_{v}" for k, v in sorted(self.weights.items()))
        return f"{self.heuristic_type.value}_{self.name}_{params_key}_{weights_key}"
    
    def validate(self) -> List[str]:
        """Validate heuristic configuration"""
        errors = []
        
        if not self.name:
            errors.append("Heuristic name cannot be empty")
        
        # Validate weights sum to 1 for composite heuristics
        if self.weights:
            weight_sum = sum(self.weights.values())
            if not (0.99 <= weight_sum <= 1.01):  # Allow small floating point errors
                errors.append(f"Weights sum to {weight_sum:.3f}, should sum to 1.0")
        
        return errors
    
    def get_parameter_value(self, name: str, default: Any = None) -> Any:
        """Get parameter value by name"""
        return self.parameters.get(name, default)


@dataclass
class HeuristicSuiteConfig(BaseConfig):
    """Configuration for a suite of heuristics to test"""
    
    heuristics: List[HeuristicConfig] = field(default_factory=list)
    
    def __post_init__(self):
        """Convert nested dictionaries to proper objects"""
        # Convert heuristic dictionaries to HeuristicConfig objects
        if self.heuristics and len(self.heuristics) > 0:
            if isinstance(self.heuristics[0], dict):
                converted_heuristics = []
                for heuristic_dict in self.heuristics:
                    if isinstance(heuristic_dict, dict):
                        # Ensure heuristic_type is Enum
                        if "heuristic_type" in heuristic_dict and isinstance(heuristic_dict["heuristic_type"], str):
                            heuristic_dict["heuristic_type"] = HeuristicType(heuristic_dict["heuristic_type"])
                        converted_heuristics.append(HeuristicConfig.from_dict(heuristic_dict))
                    else:
                        converted_heuristics.append(heuristic_dict)
                self.heuristics = converted_heuristics
    
    @classmethod
    def default_suite(cls) -> 'HeuristicSuiteConfig':
        """Get default heuristic suite"""
        return cls(
            heuristics=[
                HeuristicConfig(
                    name="Closeness",
                    heuristic_type=HeuristicType.CLOSENESS,
                    description="Focuses on closeness to 21"
                ),
                HeuristicConfig(
                    name="Aggressive",
                    heuristic_type=HeuristicType.AGGRESSIVE,
                    description="Always goes for higher values"
                ),
                HeuristicConfig(
                    name="Cautious",
                    heuristic_type=HeuristicType.CAUTIOUS,
                    description="Strongly avoids busting"
                ),
                HeuristicConfig(
                    name="Balanced",
                    heuristic_type=HeuristicType.BALANCED,
                    description="Balanced consideration of all factors"
                )
            ]
        )
    
    def add_custom_heuristic(
        self,
        name: str,
        evaluation_function: Callable,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Add a custom heuristic to the suite"""
        heuristic = HeuristicConfig(
            name=name,
            heuristic_type=HeuristicType.CUSTOM,
            description=description,
            evaluation_function=evaluation_function,
            parameters=parameters or {}
        )
        self.heuristics.append(heuristic)
    
    def get_heuristic_by_name(self, name: str) -> Optional[HeuristicConfig]:
        """Get heuristic configuration by name"""
        for heuristic in self.heuristics:
            if heuristic.name == name:
                return heuristic
        return None
    
    def get_heuristics_by_type(self, heuristic_type: HeuristicType) -> List[HeuristicConfig]:
        """Get all heuristics of specified type"""
        return [h for h in self.heuristics if h.heuristic_type == heuristic_type]
