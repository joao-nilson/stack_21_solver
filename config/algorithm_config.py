#config/algorithm_config.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .base_config import BaseConfig
from .enums import AlgorithmType

@dataclass
class AlgorithmConfig(BaseConfig):
    """Configuration for a single algorithm"""
    
     # Basic algorithm properties
    name: str
    algorithm_type: AlgorithmType
    description: str = ""
    
    # Algorithm-specific parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Performance constraints
    depth_limit: Optional[int] = None
    time_limit_seconds: Optional[float] = None
    memory_limit_mb: Optional[float] = None
    
    # Optimization flags
    use_transposition_table: bool = False
    use_move_ordering: bool = True
    use_iterative_deepening: bool = False
    
    # Custom algorithm implementation (if provided)
    custom_implementation: Optional[callable] = None
    
    def __post_init__(self):
        """Initialize default parameters"""
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        
        if self.parameters is None:
            self.parameters = {}
    
    def get_algorithm_key(self) -> str:
        """Get unique key for this algorithm configuration"""
        params_key = "_".join(f"{k}_{v}" for k, v in sorted(self.parameters.items()))
        depth_str = f"depth{self.depth_limit}" if self.depth_limit else "unlimited"
        return f"{self.algorithm_type.value}_{self.name}_{params_key}_{depth_str}"
    
    def validate(self) -> List[str]:
        """Validate algorithm configuration"""
        errors = []
        
        if not self.name:
            errors.append("Algorithm name cannot be empty")
        
        if self.depth_limit is not None and self.depth_limit <= 0:
            errors.append("Depth limit must be positive")
        
        if self.time_limit_seconds is not None and self.time_limit_seconds <= 0:
            errors.append("Time limit must be positive")
        
        if self.memory_limit_mb is not None and self.memory_limit_mb <= 0:
            errors.append("Memory limit must be positive")
        
        return errors


@dataclass
class AlgorithmSuiteConfig(BaseConfig):
    """Configuration for a suite of algorithms to test"""
    
    algorithms: List[AlgorithmConfig] = field(default_factory=list)
    
    def __post_init__(self):
        """Convert nested dictionaries to proper objects"""
        # Convert algorithm dictionaries to AlgorithmConfig objects
        if self.algorithms and isinstance(self.algorithms[0], dict):
            converted_algorithms = []
            for algo_dict in self.algorithms:
                if isinstance(algo_dict, dict):
                    # Ensure algorithm_type is Enum
                    if "algorithm_type" in algo_dict and isinstance(algo_dict["algorithm_type"], str):
                        algo_dict["algorithm_type"] = AlgorithmType(algo_dict["algorithm_type"])
                    converted_algorithms.append(AlgorithmConfig.from_dict(algo_dict))
                else:
                    converted_algorithms.append(algo_dict)
            self.algorithms = converted_algorithms
    
    # Default algorithm configurations
    @classmethod
    def default_suite(cls) -> 'AlgorithmSuiteConfig':
        """Get default algorithm suite"""
        return cls(
            algorithms=[
                AlgorithmConfig(
                    algorithm_type=AlgorithmType.MINIMAX,
                    name="Minimax-Basic",
                    description="Standard minimax without optimizations",
                    depth_limit=None,
                    use_transposition_table=False,
                    use_move_ordering=False
                ),
                AlgorithmConfig(
                    algorithm_type=AlgorithmType.MINIMAX,
                    name="Minimax-Optimized",
                    description="Minimax with transposition table",
                    depth_limit=None,
                    use_transposition_table=True,
                    use_move_ordering=True,
                    parameters={"transposition_table_size": 10000}
                ),
                AlgorithmConfig(
                    algorithm_type=AlgorithmType.ALPHA_BETA,
                    name="AlphaBeta-Basic",
                    description="Alpha-beta pruning without move ordering",
                    depth_limit=None,
                    use_move_ordering=False,
                    parameters={"use_killer_moves": False}
                ),
                AlgorithmConfig(
                    algorithm_type=AlgorithmType.ALPHA_BETA,
                    name="AlphaBeta-Optimized",
                    description="Alpha-beta with full optimizations",
                    depth_limit=None,
                    use_move_ordering=True,
                    parameters={
                        "use_killer_moves": True,
                        "use_history_heuristic": True
                    }
                ),
                AlgorithmConfig(
                    algorithm_type=AlgorithmType.ALPHA_BETA,
                    name="AlphaBeta-Limited",
                    description="Alpha-beta with depth limit 5",
                    depth_limit=5,
                    use_move_ordering=True
                ),
                AlgorithmConfig(
                    algorithm_type=AlgorithmType.ALPHA_BETA,
                    name="AlphaBeta-Limited-Deep",
                    description="Alpha-beta with depth limit 8",
                    depth_limit=8,
                    use_move_ordering=True
                )
            ]
        )
    
    def get_algorithm_by_name(self, name: str) -> Optional[AlgorithmConfig]:
        """Get algorithm configuration by name"""
        for algo in self.algorithms:
            if algo.name == name:
                return algo
        return None
    
    def get_algorithms_by_type(self, algo_type: AlgorithmType) -> List[AlgorithmConfig]:
        """Get all algorithms of specified type"""
        return [algo for algo in self.algorithms if algo.algorithm_type == algo_type]
    
    def add_algorithm(self, algorithm: AlgorithmConfig):
        """Add an algorithm to the suite"""
        self.algorithms.append(algorithm)
    
    def remove_algorithm(self, name: str):
        """Remove an algorithm from the suite by name"""
        self.algorithms = [algo for algo in self.algorithms if algo.name != name]
