from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path  # ADD THIS IMPORT
import hashlib
from .algorithm_config import AlgorithmSuiteConfig
from .heuristic_config import HeuristicSuiteConfig
from .stack_config import StackSuiteConfig
from .base_config import BaseConfig


@dataclass
class ExperimentConstraints(BaseConfig):
    """Resource and performance constraints for experiments"""
    
    # Time constraints
    max_total_time_seconds: Optional[float] = 3600  # 1 hour
    max_time_per_experiment_seconds: Optional[float] = 60  # 1 minute
    
    # Memory constraints
    max_memory_mb: Optional[float] = 1024  # 1 GB
    
    # Computation constraints
    max_total_experiments: Optional[int] = None
    max_depth_per_experiment: Optional[int] = None
    
    # Parallel execution
    max_parallel_workers: int = 4
    use_parallel_execution: bool = True
    
    # Early stopping
    early_stopping_enabled: bool = True
    early_stopping_patience: int = 10  # Stop if no improvement for N experiments
    early_stopping_metric: str = "nodes_evaluated"  # Metric to monitor
    
    def validate(self) -> List[str]:
        """Validate constraints"""
        errors = []
        
        if self.max_total_time_seconds is not None and self.max_total_time_seconds <= 0:
            errors.append("Max total time must be positive")
        
        if self.max_time_per_experiment_seconds is not None and self.max_time_per_experiment_seconds <= 0:
            errors.append("Max time per experiment must be positive")
        
        if self.max_memory_mb is not None and self.max_memory_mb <= 0:
            errors.append("Max memory must be positive")
        
        if self.max_parallel_workers < 1:
            errors.append("Must have at least 1 worker")
        
        return errors


@dataclass
class ExperimentMetrics(BaseConfig):
    """Metrics to collect during experiments"""
    
    # Performance metrics
    collect_performance_metrics: bool = True
    performance_metrics: List[str] = field(default_factory=lambda: [
        "execution_time",
        "nodes_evaluated",
        "pruned_branches",
        "pruning_efficiency",
        "memory_usage_mb",
        "peak_memory_mb",
        "nodes_per_second",
        "branching_factor",
        "tree_depth",
        "transposition_hits",
        "alpha_beta_cutoffs"
    ])
    
    # Game quality metrics
    collect_game_metrics: bool = True
    game_metrics: List[str] = field(default_factory=lambda: [
        "final_total",
        "distance_from_21",
        "win",
        "bust",
        "moves_count",
        "avg_move_value",
        "max_move_value",
        "min_move_value",
        "total_value_taken",
        "total_value_discarded",
        "risk_factor",
        "game_completion"  # percentage of stack used
    ])
    
    # Algorithm-specific metrics
    collect_algorithm_metrics: bool = True
    algorithm_metrics: Dict[str, List[str]] = field(default_factory=lambda: {
        "minimax": ["transposition_table_size", "memoization_hits"],
        "alphabeta": ["killer_move_hits", "history_heuristic_score"]
    })
    
    # Statistical metrics
    collect_statistical_metrics: bool = True
    statistical_metrics: List[str] = field(default_factory=lambda: [
        "mean",
        "median",
        "std_dev",
        "min",
        "max",
        "percentile_25",
        "percentile_75",
        "confidence_95"
    ])
    
    # Aggregation settings
    aggregate_across_runs: bool = True
    aggregation_methods: List[str] = field(default_factory=lambda: [
        "mean",
        "median",
        "std",
        "min",
        "max"
    ])
    
    # Thresholds for interesting results
    interesting_thresholds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "pruning_efficiency": (0.3, 1.0),  # Interesting if > 30%
        "nodes_per_second": (1000, float('inf')),  # Interesting if > 1000 nodes/sec
        "distance_from_21": (0, 5),  # Interesting if within 5 of 21
        "win_rate": (0.5, 1.0)  # Interesting if > 50%
    })


@dataclass
class ExperimentOutput(BaseConfig):
    """Output configuration for experiments"""
    
    # Output directories
    output_base_dir: str = "experiment_results"
    results_dir: str = "results"
    logs_dir: str = "logs"
    visualizations_dir: str = "visualizations"
    reports_dir: str = "reports"
    cache_dir: str = "cache"
    
    # File formats
    results_format: str = "json"  # json, csv, parquet
    visualization_format: str = "png"  # png, svg, pdf, html
    
    # What to save
    save_raw_results: bool = True
    save_aggregated_results: bool = True
    save_visualizations: bool = True
    save_reports: bool = True
    save_logs: bool = True
    save_cache: bool = True
    
    # Compression
    compress_results: bool = True
    compression_level: int = 6
    
    # Database
    use_database: bool = True
    database_type: str = "sqlite"  # sqlite, postgres, mysql
    database_path: str = "results.db"
    
    # Visualization settings
    generate_comparison_charts: bool = True
    generate_performance_plots: bool = True
    generate_heatmaps: bool = True
    generate_radar_charts: bool = True
    generate_interactive_dashboards: bool = True
    
    # Report settings
    generate_executive_summary: bool = True
    generate_detailed_report: bool = True
    generate_markdown_report: bool = True
    generate_pdf_report: bool = False
    
    def get_output_paths(self) -> Dict[str, str]:
        """Get all output paths as dictionary"""
        base = Path(self.output_base_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        paths = {
            "base": str(base),
            "timestamp": timestamp,
            "results": str(base / self.results_dir / timestamp),
            "logs": str(base / self.logs_dir / timestamp),
            "visualizations": str(base / self.visualizations_dir / timestamp),
            "reports": str(base / self.reports_dir / timestamp),
            "cache": str(base / self.cache_dir),
            "database": str(base / self.database_path)
        }
        
        # Create directories
        for path in paths.values():
            if path and "cache" not in path and "database" not in path:
                Path(path).mkdir(parents=True, exist_ok=True)
        
        return paths


@dataclass
class ExperimentConfig(BaseConfig):
    """Main configuration for comprehensive experiments"""
    
    # Basic experiment info
    name: str = "algorithm_benchmark"
    description: str = "Comprehensive algorithm benchmarking"
    version: str = "1.0.0"
    author: str = "Stack21 Analyzer"
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Experiment components
    algorithms: AlgorithmSuiteConfig = field(default_factory=AlgorithmSuiteConfig.default_suite)
    heuristics: HeuristicSuiteConfig = field(default_factory=HeuristicSuiteConfig.default_suite)
    stacks: StackSuiteConfig = field(default_factory=StackSuiteConfig.comprehensive_suite)
    
    # Experiment design
    constraints: ExperimentConstraints = field(default_factory=ExperimentConstraints)
    metrics: ExperimentMetrics = field(default_factory=ExperimentMetrics)
    output: ExperimentOutput = field(default_factory=ExperimentOutput)
    
    # Cross-product configuration
    test_all_combinations: bool = True
    combinations_to_test: Optional[List[Dict[str, str]]] = None
    
    # Reproducibility
    random_seed: Optional[int] = 42
    enforce_reproducibility: bool = True
    
    # Filtering and sampling
    max_experiments: Optional[int] = None
    sample_experiments: bool = False
    sample_size: Optional[int] = 100
    sampling_strategy: str = "random"  # random, stratified, latin_hypercube
    
    # Validation
    validate_before_run: bool = True
    validate_after_run: bool = True
    
    def __post_init__(self):
        """Initialize experiment configuration"""
        # Set random seed for reproducibility
        if self.random_seed is not None:
            import random
            import numpy as np
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)
    
    def get_experiment_id(self) -> str:
        """Generate unique experiment ID"""
        config_hash = hashlib.md5(
            self.to_json().encode('utf-8')
        ).hexdigest()[:8]
        
        timestamp = self.timestamp.strftime("%Y%m%d_%H%M%S")
        
        return f"{self.name}_{timestamp}_{config_hash}"
    
    def get_total_experiments(self) -> int:
        """Calculate total number of experiments"""
        if not self.test_all_combinations:
            if self.combinations_to_test:
                return len(self.combinations_to_test)
            else:
                return 0
        
        # Calculate cross-product size
        total = 0
        
        for algorithm in self.algorithms.algorithms:
            for heuristic in self.heuristics.heuristics:
                for stack in self.stacks.stacks:
                    total += 1
        
        return total
    
    def get_experiment_combinations(self) -> List[Dict[str, Any]]:
        """Get all experiment combinations to run"""
        combinations = []
        
        if not self.test_all_combinations:
            if self.combinations_to_test:
                return self.combinations_to_test
            else:
                return []
        
        # Generate cross-product
        for algorithm in self.algorithms.algorithms:
            for heuristic in self.heuristics.heuristics:
                for stack in self.stacks.stacks:
                    combination = {
                        "algorithm": algorithm,
                        "heuristic": heuristic,
                        "stack": stack,
                        "combination_id": (
                            f"{algorithm.get_algorithm_key()}_"
                            f"{heuristic.get_heuristic_key()}_"
                            f"{stack.get_stack_key()}"
                        )
                    }
                    combinations.append(combination)
        
        # Apply sampling if requested
        if self.sample_experiments and self.sample_size is not None:
            combinations = self._sample_combinations(combinations)
        
        # Apply max limit if specified
        if self.max_experiments is not None:
            combinations = combinations[:self.max_experiments]
        
        return combinations
    
    def _sample_combinations(self, combinations: List[Dict]) -> List[Dict]:
        """Sample combinations based on sampling strategy"""
        if not combinations:
            return combinations
        
        if self.sampling_strategy == "random":
            import random
            return random.sample(combinations, min(self.sample_size, len(combinations)))
        
        elif self.sampling_strategy == "stratified":
            # Stratify by algorithm type, heuristic type, and stack length
            return self._stratified_sample(combinations)
        
        elif self.sampling_strategy == "latin_hypercube":
            # Latin hypercube sampling across dimensions
            return self._latin_hypercube_sample(combinations)
        
        else:
            raise ValueError(f"Unknown sampling strategy: {self.sampling_strategy}")
    
    def _stratified_sample(self, combinations: List[Dict]) -> List[Dict]:
        """Stratified sampling to ensure representation"""
        # Group by key dimensions
        groups = {}
        
        for combo in combinations:
            key = (
                combo["algorithm"].algorithm_type.value,
                combo["heuristic"].heuristic_type.value,
                combo["stack"].length // 4  # Bucket stack lengths
            )
            
            if key not in groups:
                groups[key] = []
            groups[key].append(combo)
        
        # Sample proportionally from each group
        sampled = []
        target_per_group = max(1, self.sample_size // len(groups))
        
        for group_combos in groups.values():
            import random
            sampled.extend(
                random.sample(
                    group_combos,
                    min(target_per_group, len(group_combos))
                )
            )
        
        return sampled
    
    def validate(self) -> List[str]:
        """Validate entire experiment configuration"""
        errors = []
        
        # Validate components
        errors.extend(self.algorithms.validate())
        errors.extend(self.heuristics.validate())
        errors.extend(self.stacks.validate())
        errors.extend(self.constraints.validate())
        
        # Check for empty configurations
        if not self.algorithms.algorithms:
            errors.append("No algorithms configured")
        
        if not self.heuristics.heuristics:
            errors.append("No heuristics configured")
        
        if not self.stacks.stacks:
            errors.append("No stacks configured")
        
        # Check total experiments
        total_experiments = self.get_total_experiments()
        if total_experiments == 0:
            errors.append("No experiment combinations to test")
        
        if self.constraints.max_total_experiments is not None:
            if total_experiments > self.constraints.max_total_experiments:
                errors.append(
                    f"Total experiments ({total_experiments}) exceeds "
                    f"maximum ({self.constraints.max_total_experiments})"
                )
        
        # Check time constraints
        if self.constraints.max_time_per_experiment_seconds is not None:
            if self.constraints.max_time_per_experiment_seconds < 0.1:
                errors.append("Time per experiment too small (< 0.1s)")
        
        return errors
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of configuration"""
        return {
            "experiment_name": self.name,
            "experiment_id": self.get_experiment_id(),
            "total_algorithms": len(self.algorithms.algorithms),
            "total_heuristics": len(self.heuristics.heuristics),
            "total_stacks": len(self.stacks.stacks),
            "total_experiments": self.get_total_experiments(),
            "algorithm_types": list(set(
                a.algorithm_type.value for a in self.algorithms.algorithms
            )),
            "heuristic_types": list(set(
                h.heuristic_type.value for h in self.heuristics.heuristics
            )),
            "stack_types": list(set(
                s.stack_type.value for s in self.stacks.stacks
            )),
            "stack_lengths": list(set(
                s.length for s in self.stacks.stacks
            )),
            "constraints": {
                "max_total_time": self.constraints.max_total_time_seconds,
                "max_time_per_experiment": self.constraints.max_time_per_experiment_seconds,
                "max_parallel_workers": self.constraints.max_parallel_workers
            },
            "timestamp": self.timestamp.isoformat()
        }