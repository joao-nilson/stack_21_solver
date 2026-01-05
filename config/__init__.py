# config/__init__.py
"""
Unified configuration management for Stack-based 21 Solver
"""

# Import enums first (no dependencies)
from .enums import (
    AlgorithmType,
    HeuristicType,
    StackType,
    StackGenerationStrategy
)

# Import base config (only depends on enums)
from .base_config import BaseConfig

# Import specific config classes
from .algorithm_config import (
    AlgorithmConfig,
    AlgorithmSuiteConfig
)

from .heuristic_config import (
    HeuristicConfig,
    HeuristicSuiteConfig
)

from .stack_config import (
    StackGenerationConfig,
    StackSuiteConfig
)

from .experiment_config import (
    ExperimentConfig,
    ExperimentConstraints
)

# Import manager last (depends on everything else)
from .config_manager import ConfigManager

__all__ = [
    # Enums
    'AlgorithmType',
    'HeuristicType',
    'StackType',
    'StackGenerationStrategy',
    
    # Base
    'BaseConfig',
    
    # Algorithm configs
    'AlgorithmConfig',
    'AlgorithmSuiteConfig',
    
    # Heuristic configs
    'HeuristicConfig',
    'HeuristicSuiteConfig',
    
    # Stack configs
    'StackGenerationConfig',
    'StackSuiteConfig',
    
    # Experiment configs
    'ExperimentConfig',
    'ExperimentConstraints',
    
    # Manager
    'ConfigManager'
]
