#/config/stack_config
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from .base_config import BaseConfig
from .enums import StackType, StackGenerationStrategy


@dataclass
class StackGenerationConfig(BaseConfig):
    """Configuration for generating stacks"""
    
    stack_type: StackType
    length: int
    generation_strategy: StackGenerationStrategy = StackGenerationStrategy.UNIFORM
    
    # Optional name for identification
    name: Optional[str] = None
    
    # Parameters for generation
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Fixed stack (if provided instead of generation)
    fixed_stack: Optional[List[int]] = None
    
    def __post_init__(self):
        """Initialize with validation"""
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        
        # Initialize empty dicts if None
        if self.parameters is None:
            self.parameters = {}
        
        # Validate length
        if self.length < 2:
            raise ValueError(f"Stack length must be at least 2, got {self.length}")
        
        # Validate fixed stack if provided
        if self.fixed_stack is not None:
            if len(self.fixed_stack) != self.length:
                raise ValueError(
                    f"Fixed stack length {len(self.fixed_stack)} "
                    f"doesn't match configured length {self.length}"
                )
            
            # Validate stack values are between 1 and 6
            for value in self.fixed_stack:
                if not 1 <= value <= 6:
                    raise ValueError(f"Stack value {value} must be between 1 and 6")
    
    def _set_default_parameters(self):
        """Set default parameters for stack generation"""
        if self.stack_type == StackType.RANDOM:
            self.parameters = {
                "min_value": 1,
                "max_value": 6,
                "distribution": "uniform"
            }
        
        elif self.stack_type == StackType.BALANCED:
            self.parameters = {
                "balance_method": "equal_distribution",
                "max_imbalance": 1
            }
        
        elif self.stack_type == StackType.BIASED_HIGH:
            self.parameters = {
                "bias_value": 6,
                "bias_strength": 0.7,  # 70% chance of bias value
                "other_distribution": "uniform"
            }
        
        elif self.stack_type == StackType.BIASED_LOW:
            self.parameters = {
                "bias_value": 1,
                "bias_strength": 0.7,
                "other_distribution": "uniform"
            }
        
        elif self.stack_type == StackType.ALTERNATING:
            self.parameters = {
                "pattern": [1, 6, 2, 5, 3, 4],
                "repeat_pattern": True
            }
        
        elif self.stack_type == StackType.INCREASING:
            self.parameters = {
                "start_value": 1,
                "increment": 0.5,  # Can be fractional for patterns
                "wrap_around": True
            }
    
    def get_stack_key(self) -> str:
        """Get unique key for this stack configuration"""
        if self.fixed_stack:
            return f"fixed_{'_'.join(str(x) for x in self.fixed_stack)}"
        
        params_key = "_".join(f"{k}_{v}" for k, v in sorted(self.parameters.items()))
        return f"{self.stack_type.value}_{self.length}_{params_key}"
    
    def validate(self) -> List[str]:
        """Validate stack configuration"""
        errors = super().validate()
        
        if self.length < 2:
            errors.append(f"Stack length {self.length} must be at least 2")
        
        if self.length % 2 != 0:
            errors.append(f"Stack length {self.length} should be even for paired moves")
        
        # Validate parameters
        if self.stack_type == StackType.BIASED_HIGH:
            bias = self.parameters.get("bias_value", 6)
            if not 1 <= bias <= 6:
                errors.append(f"Bias value {bias} must be between 1 and 6")
            
            strength = self.parameters.get("bias_strength", 0.7)
            if not 0 <= strength <= 1:
                errors.append(f"Bias strength {strength} must be between 0 and 1")
        
        elif self.stack_type == StackType.BIASED_LOW:
            bias = self.parameters.get("bias_value", 1)
            if not 1 <= bias <= 6:
                errors.append(f"Bias value {bias} must be between 1 and 6")
        
        return errors
    
    def generate_stack(self) -> List[int]:
        """Generate stack based on configuration"""
        if self.fixed_stack is not None:
            return self.fixed_stack.copy()
        
        if self.stack_type == StackType.RANDOM:
            return self._generate_random_stack()
        
        elif self.stack_type == StackType.BALANCED:
            return self._generate_balanced_stack()
        
        elif self.stack_type in [StackType.BIASED_HIGH, StackType.BIASED_LOW]:
            return self._generate_biased_stack()
        
        elif self.stack_type == StackType.ALTERNATING:
            return self._generate_alternating_stack()
        
        elif self.stack_type == StackType.INCREASING:
            return self._generate_increasing_stack()
        
        else:
            raise ValueError(f"Unknown stack type: {self.stack_type}")
    
    def _generate_random_stack(self) -> List[int]:
        """Generate random stack"""
        import random
        min_val = self.parameters.get("min_value", 1)
        max_val = self.parameters.get("max_value", 6)
        
        return [random.randint(min_val, max_val) for _ in range(self.length)]
    
    def _generate_balanced_stack(self) -> List[int]:
        """Generate balanced stack with equal distribution"""
        import random
        
        # Create a balanced distribution
        values = list(range(1, 7))
        repetitions = (self.length // 6) + 1
        
        stack = []
        for _ in range(repetitions):
            random.shuffle(values)
            stack.extend(values)
        
        # Trim to desired length and shuffle
        stack = stack[:self.length]
        random.shuffle(stack)
        
        return stack
    
    def _generate_biased_stack(self) -> List[int]:
        """Generate biased stack"""
        import random
        
        bias_value = self.parameters.get("bias_value", 6 if self.stack_type == StackType.BIASED_HIGH else 1)
        bias_strength = self.parameters.get("bias_strength", 0.7)
        
        stack = []
        for _ in range(self.length):
            if random.random() < bias_strength:
                stack.append(bias_value)
            else:
                # Generate other values
                other_values = [v for v in range(1, 7) if v != bias_value]
                stack.append(random.choice(other_values))
        
        return stack
    
    def _generate_alternating_stack(self) -> List[int]:
        """Generate alternating pattern stack"""
        pattern = self.parameters.get("pattern", [1, 6, 2, 5, 3, 4])
        repeat_pattern = self.parameters.get("repeat_pattern", True)
        
        if repeat_pattern:
            repetitions = (self.length // len(pattern)) + 1
            stack = []
            for _ in range(repetitions):
                stack.extend(pattern)
            return stack[:self.length]
        else:
            # Extend pattern to desired length
            if len(pattern) >= self.length:
                return pattern[:self.length]
            else:
                # Pad with last value
                return pattern + [pattern[-1]] * (self.length - len(pattern))
    
    def _generate_increasing_stack(self) -> List[int]:
        """Generate increasing pattern stack"""
        start = self.parameters.get("start_value", 1)
        increment = self.parameters.get("increment", 0.5)
        wrap_around = self.parameters.get("wrap_around", True)
        
        stack = []
        current = start
        
        for _ in range(self.length):
            # Round to nearest integer between 1 and 6
            value = int(round(current))
            value = max(1, min(6, value))  # Clamp to 1-6
            stack.append(value)
            
            current += increment
            
            # Wrap around if needed
            if wrap_around and current > 6:
                current = 1
        
        return stack


@dataclass
class StackSuiteConfig(BaseConfig):
    """Configuration for a suite of stacks to test"""
    
    stacks: List[StackGenerationConfig] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert nested dictionaries to proper objects"""
        # Convert stack dictionaries to StackGenerationConfig objects
        if self.stacks and isinstance(self.stacks[0], dict):
            converted_stacks = []
            for stack_dict in self.stacks:
                if isinstance(stack_dict, dict):
                    # Ensure stack_type is Enum
                    if "stack_type" in stack_dict and isinstance(stack_dict["stack_type"], str):
                        stack_dict["stack_type"] = StackType(stack_dict["stack_type"])
                    converted_stacks.append(StackGenerationConfig.from_dict(stack_dict))
                else:
                    converted_stacks.append(stack_dict)
            self.stacks = converted_stacks
        
        # Calculate statistics
        self._calculate_statistics()
    
    @classmethod
    def comprehensive_suite(cls) -> 'StackSuiteConfig':
        """Create a comprehensive stack suite for benchmarking"""
        suite = cls()
        
        # Different stack lengths for scalability testing
        lengths = [4, 6, 8, 10, 12, 16, 20, 24]
        
        # Different stack types
        stack_types = [
            (StackType.RANDOM, "Random"),
            (StackType.BALANCED, "Balanced"),
            (StackType.BIASED_HIGH, "Biased-High"),
            (StackType.BIASED_LOW, "Biased-Low"),
            (StackType.ALTERNATING, "Alternating")
        ]
        
        # Create 3 instances of each combination for statistical significance
        for stack_type, name_prefix in stack_types:
            for length in lengths:
                for i in range(3):  # 3 instances each
                    stack_config = StackGenerationConfig(
                        stack_type=stack_type,
                        length=length,
                        parameters={}
                    )
                    stack_config.name = f"{name_prefix}-{length}-{i+1}"
                    suite.stacks.append(stack_config)
        
        # Add some fixed interesting stacks
        fixed_stacks = [
            ([3, 5, 2, 6], "Simple-4"),
            ([6, 6, 6, 3, 2, 4], "Winning-6"),
            ([1, 1, 2, 2, 3, 3, 4, 4], "Safe-8"),
            ([6, 1, 6, 1, 6, 1, 6, 1], "Extreme-8"),
            ([1, 6, 2, 5, 3, 4, 1, 6, 2, 5], "Pattern-10")
        ]
        
        for stack_values, name in fixed_stacks:
            stack_config = StackGenerationConfig(
                stack_type=StackType.CUSTOM,
                length=len(stack_values),
                fixed_stack=stack_values
            )
            stack_config.name = f"Fixed-{name}"
            suite.stacks.append(stack_config)
        
        # Calculate suite statistics
        suite._calculate_statistics()
        
        return suite
    
    @classmethod
    def quick_suite(cls) -> 'StackSuiteConfig':
        """Create a quick stack suite for testing"""
        suite = cls()
        
        # Just a few representative stacks
        stacks = [
            StackGenerationConfig(
                stack_type=StackType.RANDOM,
                length=6,
                name="Random-6"
            ),
            StackGenerationConfig(
                stack_type=StackType.BALANCED,
                length=8,
                name="Balanced-8"
            ),
            StackGenerationConfig(
                stack_type=StackType.BIASED_HIGH,
                length=10,
                name="BiasedHigh-10"
            ),
            StackGenerationConfig(
                stack_type=StackType.ALTERNATING,
                length=12,
                name="Alternating-12"
            )
        ]
        
        suite.stacks = stacks
        suite._calculate_statistics()
        
        return suite
    
    def _calculate_statistics(self):
        """Calculate statistics about the stack suite"""
        if not self.stacks:
            self.statistics = {}
            return
        
        # Generate all stacks to calculate statistics
        all_stacks = []
        for stack_config in self.stacks:
            try:
                stack = stack_config.generate_stack()
                all_stacks.append(stack)
            except:
                continue
        
        if not all_stacks:
            self.statistics = {}
            return
        
        # Calculate statistics
        all_values = [value for stack in all_stacks for value in stack]
        
        self.statistics = {
            "total_stacks": len(self.stacks),
            "total_values": len(all_values),
            "avg_stack_length": np.mean([len(stack) for stack in all_stacks]),
            "min_value": min(all_values),
            "max_value": max(all_values),
            "mean_value": np.mean(all_values),
            "median_value": np.median(all_values),
            "std_value": np.std(all_values),
            "value_distribution": {
                i: all_values.count(i) for i in range(1, 7)
            }
        }
    
    def get_stack_by_name(self, name: str) -> Optional[StackGenerationConfig]:
        """Get stack configuration by name"""
        for stack in self.stacks:
            if getattr(stack, 'name', None) == name:
                return stack
        return None
    
    def get_stacks_by_type(self, stack_type: StackType) -> List[StackGenerationConfig]:
        """Get all stacks of specified type"""
        return [s for s in self.stacks if s.stack_type == stack_type]
    
    def get_stacks_by_length(self, length: int) -> List[StackGenerationConfig]:
        """Get all stacks of specified length"""
        return [s for s in self.stacks if s.length == length]
    
    def add_stack(self, stack: StackGenerationConfig, name: str = ""):
        """Add a stack to the suite"""
        if name:
            stack.name = name
        self.stacks.append(stack)
        self._calculate_statistics()
