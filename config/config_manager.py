# config/config_manager.py (simplified version)
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import asdict
import copy

from .experiment_config import ExperimentConfig
from .algorithm_config import AlgorithmSuiteConfig
from .heuristic_config import HeuristicSuiteConfig
from .stack_config import StackSuiteConfig


class ConfigManager:
    """Manager for handling configuration files and presets"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True, parents=True)
    
    def get_preset_names(self) -> List[str]:
        """Get list of available preset names"""
        return ["quick_test", "comprehensive_benchmark", "algorithm_comparison", 
                "heuristic_analysis", "scalability_study"]
    
    def load_preset(self, preset_name: str) -> ExperimentConfig:
        """Load a preset configuration"""
        if preset_name == "quick_test":
            return self._create_quick_test_config()
        elif preset_name == "comprehensive_benchmark":
            return self._create_comprehensive_benchmark_config()
        elif preset_name == "algorithm_comparison":
            return self._create_algorithm_comparison_config()
        elif preset_name == "heuristic_analysis":
            return self._create_heuristic_analysis_config()
        elif preset_name == "scalability_study":
            return self._create_scalability_study_config()
        else:
            available = ", ".join(self.get_preset_names())
            raise ValueError(f"Unknown preset: {preset_name}. Available: {available}")
    
    def _create_quick_test_config(self) -> ExperimentConfig:
        """Create quick test configuration"""
        from .enums import AlgorithmType, HeuristicType, StackType
        from .algorithm_config import AlgorithmConfig
        from .heuristic_config import HeuristicConfig
        from .stack_config import StackGenerationConfig
        from .experiment_config import ExperimentConstraints
        
        return ExperimentConfig(
            name="Quick Test",
            description="Quick test of basic algorithms and heuristics",
            algorithms=AlgorithmSuiteConfig(
                algorithms=[
                    AlgorithmConfig(
                        name="Minimax-Basic",
                        algorithm_type=AlgorithmType.MINIMAX,
                        description="Standard minimax",
                        depth_limit=4
                    ),
                    AlgorithmConfig(
                        name="AlphaBeta-Basic",
                        algorithm_type=AlgorithmType.ALPHA_BETA,
                        description="Alpha-beta pruning",
                        depth_limit=4
                    )
                ]
            ),
            heuristics=HeuristicSuiteConfig(
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
                    )
                ]
            ),
            stacks=StackSuiteConfig(
                stacks=[
                    StackGenerationConfig(
                        stack_type=StackType.RANDOM,
                        length=6,
                        name="Random-6"
                    ),
                    StackGenerationConfig(
                        stack_type=StackType.BALANCED,
                        length=8,
                        name="Balanced-8"
                    )
                ]
            ),
            constraints=ExperimentConstraints(
                max_total_time_seconds=60,
                max_time_per_experiment_seconds=5
            )
        )
    
    def _create_comprehensive_benchmark_config(self) -> ExperimentConfig:
        """Create comprehensive benchmark configuration"""
        from .enums import AlgorithmType, HeuristicType, StackType
        from .algorithm_config import AlgorithmConfig
        from .heuristic_config import HeuristicConfig
        from .stack_config import StackGenerationConfig
        from .experiment_config import ExperimentConstraints
        
        return ExperimentConfig(
            name="Comprehensive Benchmark",
            description="Comprehensive benchmarking of all algorithms and heuristics",
            algorithms=AlgorithmSuiteConfig(
                algorithms=[
                    AlgorithmConfig(
                        name="Minimax-Basic",
                        algorithm_type=AlgorithmType.MINIMAX,
                        description="Standard minimax without optimizations",
                        depth_limit=None,
                        use_transposition_table=False,
                        use_move_ordering=False
                    ),
                    AlgorithmConfig(
                        name="Minimax-Optimized",
                        algorithm_type=AlgorithmType.MINIMAX,
                        description="Minimax with transposition table",
                        depth_limit=None,
                        use_transposition_table=True,
                        use_move_ordering=True,
                        parameters={"transposition_table_size": 10000}
                    ),
                    AlgorithmConfig(
                        name="AlphaBeta-Basic",
                        algorithm_type=AlgorithmType.ALPHA_BETA,
                        description="Alpha-beta pruning without move ordering",
                        depth_limit=None,
                        use_move_ordering=False,
                        parameters={"use_killer_moves": False}
                    ),
                    AlgorithmConfig(
                        name="AlphaBeta-Optimized",
                        algorithm_type=AlgorithmType.ALPHA_BETA,
                        description="Alpha-beta with full optimizations",
                        depth_limit=None,
                        use_move_ordering=True,
                        parameters={
                            "use_killer_moves": True,
                            "use_history_heuristic": True
                        }
                    )
                ]
            ),
            heuristics=HeuristicSuiteConfig(
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
            ),
            stacks=StackSuiteConfig(
                stacks=[
                    StackGenerationConfig(
                        stack_type=StackType.RANDOM,
                        length=8,
                        name="Random-8"
                    ),
                    StackGenerationConfig(
                        stack_type=StackType.RANDOM,
                        length=12,
                        name="Random-12"
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
                    )
                ]
            ),
            constraints=ExperimentConstraints(
                max_total_time_seconds=3600,
                max_time_per_experiment_seconds=30,
                max_parallel_workers=4
            )
        )
    
    def _create_algorithm_comparison_config(self) -> ExperimentConfig:
        """Create algorithm comparison configuration"""
        from .enums import AlgorithmType, HeuristicType, StackType
        
        return ExperimentConfig(
            name="Algorithm Comparison",
            description="Compare Minimax vs Alpha-Beta with different configurations",
            algorithms=AlgorithmSuiteConfig(
                algorithms=[
                    {
                        "algorithm_type": AlgorithmType.MINIMAX,
                        "name": "Minimax-NoOpt",
                        "description": "Minimax without optimizations",
                        "use_transposition_table": False,
                        "use_move_ordering": False
                    },
                    {
                        "algorithm_type": AlgorithmType.MINIMAX,
                        "name": "Minimax-Transposition",
                        "description": "Minimax with transposition table",
                        "use_transposition_table": True,
                        "use_move_ordering": False
                    },
                    {
                        "algorithm_type": AlgorithmType.MINIMAX,
                        "name": "Minimax-FullOpt",
                        "description": "Minimax with all optimizations",
                        "use_transposition_table": True,
                        "use_move_ordering": True
                    },
                    {
                        "algorithm_type": AlgorithmType.ALPHA_BETA,
                        "name": "AlphaBeta-NoOpt",
                        "description": "Alpha-beta without optimizations",
                        "use_move_ordering": False
                    },
                    {
                        "algorithm_type": AlgorithmType.ALPHA_BETA,
                        "name": "AlphaBeta-Optimized",
                        "description": "Alpha-beta with move ordering",
                        "use_move_ordering": True
                    }
                ]
            ),
            heuristics=HeuristicSuiteConfig(
                heuristics=[
                    {
                        "heuristic_type": HeuristicType.BALANCED,
                        "name": "Balanced",
                        "description": "Balanced consideration of all factors"
                    }
                ]
            ),
            stacks=StackSuiteConfig(
                stacks=[
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 6,
                        "name": "Random-6"
                    },
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 8,
                        "name": "Random-8"
                    },
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 10,
                        "name": "Random-10"
                    },
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 12,
                        "name": "Random-12"
                    }
                ]
            )
        )
    
    def _create_heuristic_analysis_config(self) -> ExperimentConfig:
        """Create heuristic analysis configuration"""
        from .enums import AlgorithmType, HeuristicType, StackType
        
        return ExperimentConfig(
            name="Heuristic Analysis",
            description="Analyze effectiveness of different heuristics",
            algorithms=AlgorithmSuiteConfig(
                algorithms=[
                    {
                        "algorithm_type": AlgorithmType.ALPHA_BETA,
                        "name": "AlphaBeta-Optimized",
                        "description": "Alpha-beta with optimizations",
                        "use_move_ordering": True
                    }
                ]
            ),
            heuristics=HeuristicSuiteConfig(
                heuristics=[
                    {
                        "heuristic_type": HeuristicType.CLOSENESS,
                        "name": "Closeness",
                        "description": "Focuses on closeness to 21"
                    },
                    {
                        "heuristic_type": HeuristicType.AGGRESSIVE,
                        "name": "Aggressive",
                        "description": "Always goes for higher values"
                    },
                    {
                        "heuristic_type": HeuristicType.CAUTIOUS,
                        "name": "Cautious",
                        "description": "Strongly avoids busting"
                    },
                    {
                        "heuristic_type": HeuristicType.BALANCED,
                        "name": "Balanced",
                        "description": "Balanced consideration of all factors"
                    }
                ]
            ),
            stacks=StackSuiteConfig(
                stacks=[
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 8,
                        "name": "Random-8"
                    },
                    {
                        "stack_type": StackType.BALANCED,
                        "length": 8,
                        "name": "Balanced-8"
                    },
                    {
                        "stack_type": StackType.BIASED_HIGH,
                        "length": 8,
                        "name": "BiasedHigh-8"
                    },
                    {
                        "stack_type": StackType.ALTERNATING,
                        "length": 8,
                        "name": "Alternating-8"
                    }
                ]
            )
        )
    
    def _create_scalability_study_config(self) -> ExperimentConfig:
        """Create scalability study configuration"""
        from .enums import AlgorithmType, HeuristicType, StackType
        
        return ExperimentConfig(
            name="Scalability Study",
            description="Study algorithm scalability with increasing stack size",
            algorithms=AlgorithmSuiteConfig(
                algorithms=[
                    {
                        "algorithm_type": AlgorithmType.MINIMAX,
                        "name": "Minimax",
                        "description": "Standard minimax"
                    },
                    {
                        "algorithm_type": AlgorithmType.ALPHA_BETA,
                        "name": "AlphaBeta",
                        "description": "Alpha-beta pruning"
                    },
                    {
                        "algorithm_type": AlgorithmType.ALPHA_BETA,
                        "name": "AlphaBeta-Depth5",
                        "description": "Alpha-beta with depth limit 5",
                        "depth_limit": 5
                    },
                    {
                        "algorithm_type": AlgorithmType.ALPHA_BETA,
                        "name": "AlphaBeta-Depth8",
                        "description": "Alpha-beta with depth limit 8",
                        "depth_limit": 8
                    }
                ]
            ),
            heuristics=HeuristicSuiteConfig(
                heuristics=[
                    {
                        "heuristic_type": HeuristicType.BALANCED,
                        "name": "Balanced",
                        "description": "Balanced consideration of all factors"
                    }
                ]
            ),
            stacks=StackSuiteConfig(
                stacks=[
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 4,
                        "name": "Random-4"
                    },
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 6,
                        "name": "Random-6"
                    },
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 8,
                        "name": "Random-8"
                    },
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 10,
                        "name": "Random-10"
                    },
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 12,
                        "name": "Random-12"
                    },
                    {
                        "stack_type": StackType.RANDOM,
                        "length": 14,
                        "name": "Random-14"
                    }
                ]
            )
        )
    
    def save_config(self, config: ExperimentConfig, filename: str):
        """Save configuration to file"""
        filepath = self.config_dir / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(exist_ok=True, parents=True)
        
        # Save as JSON
        config.to_json(str(filepath))
    
    def load_config(self, filename: str) -> ExperimentConfig:
        """Load configuration from file"""
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        return ExperimentConfig.from_json(str(filepath))
    
    def validate_config(self, config: ExperimentConfig) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        errors = config.validate()
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "summary": config.get_config_summary(),
            "total_experiments": config.get_total_experiments()
        }
    
    def generate_config_report(self, config: ExperimentConfig) -> str:
        """Generate human-readable configuration report"""
        validation = self.validate_config(config)
        
        report_lines = [
            "=" * 80,
            f"EXPERIMENT CONFIGURATION REPORT: {config.name}",
            "=" * 80,
            f"Description: {config.description}",
            f"Experiment ID: {config.get_experiment_id()}",
            f"Timestamp: {config.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "VALIDATION:",
            f"  Status: {'VALID' if validation['is_valid'] else 'INVALID'}",
            ""
        ]
        
        if validation['errors']:
            report_lines.append("  Errors:")
            for error in validation['errors']:
                report_lines.append(f"    - {error}")
            report_lines.append("")
        
        summary = validation['summary']
        report_lines.extend([
            "CONFIGURATION SUMMARY:",
            f"  Algorithms: {summary['total_algorithms']}",
            f"  Heuristics: {summary['total_heuristics']}",
            f"  Stacks: {summary['total_stacks']}",
            f"  Total Experiments: {summary['total_experiments']}",
            "",
            "ALGORITHM TYPES:",
        ])
        
        # Get algorithm types
        algo_types = set()
        for algo in config.algorithms.algorithms:
            if hasattr(algo, 'algorithm_type'):
                algo_types.add(str(algo.algorithm_type))
        
        for algo_type in algo_types:
            count = len([
                a for a in config.algorithms.algorithms 
                if str(a.algorithm_type) == algo_type
            ])
            report_lines.append(f"  - {algo_type}: {count} algorithms")
        
        report_lines.extend([
            "",
            "STACK INFORMATION:",
            f"  Stack Types: {len(set(s.stack_type for s in config.stacks.stacks))}",
            f"  Stack Lengths: {set(s.length for s in config.stacks.stacks)}",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
# import json
# import yaml
# from pathlib import Path
# from typing import Dict, Any, Optional, List
# from dataclasses import asdict
# import copy

# from .experiment_config import ExperimentConfig
# from .algorithm_config import AlgorithmSuiteConfig
# from .heuristic_config import HeuristicSuiteConfig
# from .stack_config import StackSuiteConfig



# class ConfigManager:
#     """Manager for handling configuration files and presets"""
    
#     def __init__(self, config_dir: str = "configs"):
#         self.config_dir = Path(config_dir)
#         self.config_dir.mkdir(exist_ok=True, parents=True)
    
#     def get_preset_names(self) -> List[str]:
#         """Get list of available preset names"""
#         return ["quick_test", "comprehensive_benchmark", "algorithm_comparison", 
#                 "heuristic_analysis", "scalability_study"]
    
#     def load_preset(self, preset_name: str) -> ExperimentConfig:
#         """Load a preset configuration"""
#         if preset_name == "quick_test":
#             return self._create_quick_test_config()
#         elif preset_name == "comprehensive_benchmark":
#             return self._create_comprehensive_benchmark_config()
#         elif preset_name == "algorithm_comparison":
#             return self._create_algorithm_comparison_config()
#         elif preset_name == "heuristic_analysis":
#             return self._create_heuristic_analysis_config()
#         elif preset_name == "scalability_study":
#             return self._create_scalability_study_config()
#         else:
#             available = ", ".join(self.get_preset_names())
#             raise ValueError(f"Unknown preset: {preset_name}. Available: {available}")
    
#     def create_experiment_template(self, template_type: str = "basic") -> ExperimentConfig:
#         """Create an experiment configuration template"""
#         templates = {
#             "basic": {
#                 "name": "Custom Experiment",
#                 "description": "Custom experiment configuration",
#                 "algorithms": {
#                     "algorithms": [
#                         {
#                             "algorithm_type": "alphabeta",
#                             "name": "AlphaBeta-Custom",
#                             "depth_limit": None,
#                             "use_move_ordering": True
#                         }
#                     ]
#                 },
#                 "heuristics": {
#                     "heuristics": [
#                         {
#                             "heuristic_type": "balanced",
#                             "name": "Balanced-Custom"
#                         }
#                     ]
#                 },
#                 "stacks": {
#                     "stacks": [
#                         {
#                             "stack_type": "random",
#                             "length": 10,
#                             "name": "Random-10-Custom"
#                         }
#                     ]
#                 },
#                 "test_all_combinations": True,
#                 "constraints": {
#                     "max_total_time_seconds": 300,
#                     "max_time_per_experiment_seconds": 10,
#                     "max_parallel_workers": 2
#                 }
#             },
#             "algorithm_focused": {
#                 "name": "Algorithm Comparison",
#                 "description": "Compare different algorithm configurations",
#                 "algorithms": {
#                     "algorithms": [
#                         {
#                             "algorithm_type": "minimax",
#                             "name": "Minimax-Base",
#                             "depth_limit": 5
#                         },
#                         {
#                             "algorithm_type": "minimax",
#                             "name": "Minimax-TT",
#                             "depth_limit": 5,
#                             "use_transposition_table": True
#                         },
#                         {
#                             "algorithm_type": "alphabeta",
#                             "name": "AlphaBeta-Base",
#                             "depth_limit": 5
#                         },
#                         {
#                             "algorithm_type": "alphabeta",
#                             "name": "AlphaBeta-FullOpt",
#                             "depth_limit": 5,
#                             "use_move_ordering": True,
#                             "parameters": {
#                                 "use_killer_moves": True,
#                                 "use_history_heuristic": True
#                             }
#                         }
#                     ]
#                 },
#                 "heuristics": {
#                     "heuristics": [
#                         {"heuristic_type": "balanced", "name": "Balanced"}
#                     ]
#                 },
#                 "stacks": {
#                     "stacks": [
#                         {"stack_type": "random", "length": 8, "name": "Test-Stack"}
#                     ]
#                 },
#                 "test_all_combinations": True
#             },
#             "heuristic_focused": {
#                 "name": "Heuristic Evaluation",
#                 "description": "Evaluate different heuristic configurations",
#                 "algorithms": {
#                     "algorithms": [
#                         {
#                             "algorithm_type": "alphabeta",
#                             "name": "AlphaBeta-Standard",
#                             "depth_limit": 6
#                         }
#                     ]
#                 },
#                 "heuristics": {
#                     "heuristics": [
#                         {"heuristic_type": "closeness", "name": "Closeness-Moderate"},
#                         {"heuristic_type": "aggressive", "name": "Aggressive-Risky",
#                         "parameters": {"aggression_factor": 0.8}},
#                         {"heuristic_type": "cautious", "name": "Cautious-Safe",
#                         "parameters": {"safety_margin": 4}},
#                         {"heuristic_type": "balanced", "name": "Balanced-Standard"}
#                     ]
#                 },
#                 "stacks": {
#                     "stacks": [
#                         {"stack_type": "balanced", "length": 10, "name": "Balanced-10"}
#                     ]
#                 },
#                 "test_all_combinations": True
#             }
#         }
        
#         if template_type not in templates:
#             available = ", ".join(templates.keys())
#             raise ValueError(f"Unknown template: {template_type}. Available: {available}")
        
#         return self.create_config_from_dict(templates[template_type])

#     def get_preset_configs(self) -> Dict[str, ExperimentConfig]:
#         """Get all preset configurations as ExperimentConfig objects"""
#         preset_configs = {}
#         for preset_name in self.get_preset_names():
#             try:
#                 preset_configs[preset_name] = self.load_preset(preset_name)
#             except Exception as e:
#                 print(f"Warning: Failed to load preset {preset_name}: {e}")
        
#         return preset_configs

#     def list_configs(self) -> List[Dict[str, Any]]:
#         """List all saved configuration files"""
#         configs = []
#         for filepath in self.config_dir.glob("**/*"):
#             if filepath.is_file() and filepath.suffix.lower() in ['.json', '.yaml', '.yml']:
#                 try:
#                     # Try to load the config to get basic info
#                     config = self.load_config(filepath.name)
#                     configs.append({
#                         "name": filepath.name,
#                         "path": str(filepath),
#                         "size": filepath.stat().st_size,
#                         "modified": datetime.fromtimestamp(filepath.stat().st_mtime),
#                         "config_info": {
#                             "name": config.name,
#                             "description": config.description,
#                             "total_experiments": config.get_total_experiments()
#                         }
#                     })
#                 except Exception as e:
#                     configs.append({
#                         "name": filepath.name,
#                         "path": str(filepath),
#                         "size": filepath.stat().st_size,
#                         "modified": datetime.fromtimestamp(filepath.stat().st_mtime),
#                         "error": str(e)
#                     })
        
#         return configs

#     def export_config(self, config: ExperimentConfig, export_format: str = "json") -> str:
#         """Export configuration to string"""
#         if export_format.lower() == "json":
#             return json.dumps(config.to_dict(), indent=2)
#         elif export_format.lower() in ["yaml", "yml"]:
#             return yaml.dump(config.to_dict(), default_flow_style=False)
#         else:
#             raise ValueError(f"Unsupported export format: {export_format}")

#     def import_config(self, config_str: str, format: str = "json") -> ExperimentConfig:
#         """Import configuration from string"""
#         if format.lower() == "json":
#             config_dict = json.loads(config_str)
#         elif format.lower() in ["yaml", "yml"]:
#             config_dict = yaml.safe_load(config_str)
#         else:
#             raise ValueError(f"Unsupported import format: {format}")
        
#         return self.create_config_from_dict(config_dict)

#     def merge_configs(self, base_config: ExperimentConfig, 
#                     override_config: Dict[str, Any]) -> ExperimentConfig:
#         """Merge two configurations, with override_config taking precedence"""
#         base_dict = base_config.to_dict()
        
#         # Deep merge dictionaries
#         def deep_merge(base: Dict, override: Dict) -> Dict:
#             for key, value in override.items():
#                 if key in base and isinstance(base[key], dict) and isinstance(value, dict):
#                     base[key] = deep_merge(base[key], value)
#                 else:
#                     base[key] = value
#             return base
        
#         merged_dict = deep_merge(base_dict, override_config)
#         return self.create_config_from_dict(merged_dict)

#     def generate_experiment_matrix(self, config: ExperimentConfig) -> List[Dict[str, Any]]:
#         """Generate all experiment combinations from configuration"""
#         experiments = []
        
#         if config.test_all_combinations:
#             for algorithm in config.algorithms.algorithms:
#                 for heuristic in config.heuristics.heuristics:
#                     for stack in config.stacks.stacks:
#                         experiments.append({
#                             "algorithm": algorithm,
#                             "heuristic": heuristic,
#                             "stack": stack,
#                             "metadata": {
#                                 "algorithm_name": algorithm.name,
#                                 "heuristic_name": heuristic.name,
#                                 "stack_name": stack.name,
#                                 "experiment_id": f"{algorithm.name}_{heuristic.name}_{stack.name}"
#                             }
#                         })
#         else:
#             # If not testing all combinations, use first of each or some other logic
#             if (len(config.algorithms.algorithms) > 0 and 
#                 len(config.heuristics.heuristics) > 0 and 
#                 len(config.stacks.stacks) > 0):
#                 experiments.append({
#                     "algorithm": config.algorithms.algorithms[0],
#                     "heuristic": config.heuristics.heuristics[0],
#                     "stack": config.stacks.stacks[0],
#                     "metadata": {
#                         "algorithm_name": config.algorithms.algorithms[0].name,
#                         "heuristic_name": config.heuristics.heuristics[0].name,
#                         "stack_name": config.stacks.stacks[0].name,
#                         "experiment_id": f"{config.algorithms.algorithms[0].name}_{config.heuristics.heuristics[0].name}_{config.stacks.stacks[0].name}"
#                     }
#                 })
        
#         return experiments

#     def save_preset(self, preset_name: str, config: ExperimentConfig):
#         """Save a configuration as a new preset"""
#         self.presets[preset_name] = config.to_dict()
        
#         # Also save to file for persistence
#         preset_file = self.config_dir / "presets.json"
#         if preset_file.exists():
#             with open(preset_file, 'r') as f:
#                 all_presets = json.load(f)
#         else:
#             all_presets = {}
        
#         all_presets[preset_name] = config.to_dict()
        
#         with open(preset_file, 'w') as f:
#             json.dump(all_presets, f, indent=2)

#     def delete_config(self, filename: str):
#         """Delete a saved configuration file"""
#         filepath = self.config_dir / filename
#         if filepath.exists():
#             filepath.unlink()
#         else:
#             raise FileNotFoundError(f"Config file not found: {filepath}")

#     def get_config_stats(self, config: ExperimentConfig) -> Dict[str, Any]:
#         """Get detailed statistics about the configuration"""
#         validation = self.validate_config(config)
        
#         # Count algorithm types
#         algorithm_types = {}
#         for algo in config.algorithms.algorithms:
#             algo_type = algo.algorithm_type.value
#             algorithm_types[algo_type] = algorithm_types.get(algo_type, 0) + 1
        
#         # Count heuristic types
#         heuristic_types = {}
#         for heuristic in config.heuristics.heuristics:
#             heuristic_type = heuristic.heuristic_type.value
#             heuristic_types[heuristic_type] = heuristic_types.get(heuristic_type, 0) + 1
        
#         # Stack statistics
#         stack_lengths = [stack.length for stack in config.stacks.stacks]
#         stack_types = {}
#         for stack in config.stacks.stacks:
#             stack_type = stack.stack_type.value
#             stack_types[stack_type] = stack_types.get(stack_type, 0) + 1
        
#         return {
#             "basic": {
#                 "name": config.name,
#                 "description": config.description,
#                 "experiment_id": config.get_experiment_id(),
#                 "timestamp": config.timestamp.isoformat()
#             },
#             "counts": {
#                 "total_algorithms": len(config.algorithms.algorithms),
#                 "total_heuristics": len(config.heuristics.heuristics),
#                 "total_stacks": len(config.stacks.stacks),
#                 "total_experiments": config.get_total_experiments()
#             },
#             "algorithm_types": algorithm_types,
#             "heuristic_types": heuristic_types,
#             "stack_statistics": {
#                 "total_stack_types": len(stack_types),
#                 "stack_types": stack_types,
#                 "min_length": min(stack_lengths) if stack_lengths else 0,
#                 "max_length": max(stack_lengths) if stack_lengths else 0,
#                 "avg_length": sum(stack_lengths) / len(stack_lengths) if stack_lengths else 0,
#                 "total_length": sum(stack_lengths)
#             },
#             "constraints": {
#                 "max_total_time_seconds": config.constraints.max_total_time_seconds,
#                 "max_time_per_experiment_seconds": config.constraints.max_time_per_experiment_seconds,
#                 "max_parallel_workers": config.constraints.max_parallel_workers,
#                 "max_memory_mb": config.constraints.max_memory_mb
#             },
#             "validation": validation,
#             "time_estimate": self._estimate_total_time(config)
#         }

#     def _create_quick_test_preset(self) -> Dict[str, Any]:
#         """Create quick test preset configuration - FIXED"""
#         return {
#             "name": "Quick Test",
#             "description": "Quick test of basic algorithms and heuristics",
#             "algorithms": {
#                 "algorithms": [
#                     {
#                         "algorithm_type": "minimax",
#                         "name": "Minimax-Basic",
#                         "depth_limit": 4
#                     },
#                     {
#                         "algorithm_type": "alphabeta", 
#                         "name": "AlphaBeta-Basic",
#                         "depth_limit": 4
#                     }
#                 ]
#             },
#             "heuristics": {
#                 "heuristics": [
#                     {
#                         "heuristic_type": "closeness",
#                         "name": "Closeness",
#                         "description": "Focuses on closeness to 21"
#                     },
#                     {
#                         "heuristic_type": "aggressive",
#                         "name": "Aggressive", 
#                         "description": "Always goes for higher values"
#                     }
#                 ]
#             },
#             "stacks": {
#                 "stacks": [
#                     {
#                         "stack_type": "random",
#                         "length": 6,
#                         "name": "Random-6"
#                     },
#                     {
#                         "stack_type": "balanced", 
#                         "length": 8,
#                         "name": "Balanced-8"
#                     }
#                 ]
#             },
#             "constraints": {
#                 "max_total_time_seconds": 60,
#                 "max_time_per_experiment_seconds": 5
#             },
#             "test_all_combinations": True,
#             "output": {
#                 "output_base_dir": "quick_test_results"
#             }
#         }
    
#     def _create_comprehensive_benchmark_preset(self) -> Dict[str, Any]:
#         """Create comprehensive benchmark preset - FIXED"""
#         return {
#             "name": "Comprehensive Benchmark",
#             "description": "Comprehensive benchmarking of all algorithms and heuristics",
#             "algorithms": {
#                 "algorithms": [
#                     {
#                         "algorithm_type": "minimax",
#                         "name": "Minimax-Basic",
#                         "description": "Standard minimax without optimizations",
#                         "depth_limit": None,
#                         "use_transposition_table": False,
#                         "use_move_ordering": False
#                     },
#                     {
#                         "algorithm_type": "minimax",
#                         "name": "Minimax-Optimized",
#                         "description": "Minimax with transposition table",
#                         "depth_limit": None,
#                         "use_transposition_table": True,
#                         "use_move_ordering": True,
#                         "parameters": {"transposition_table_size": 10000}
#                     },
#                     {
#                         "algorithm_type": "alphabeta",
#                         "name": "AlphaBeta-Basic",
#                         "description": "Alpha-beta pruning without move ordering",
#                         "depth_limit": None,
#                         "use_move_ordering": False,
#                         "parameters": {"use_killer_moves": False}
#                     },
#                     {
#                         "algorithm_type": "alphabeta",
#                         "name": "AlphaBeta-Optimized",
#                         "description": "Alpha-beta with full optimizations",
#                         "depth_limit": None,
#                         "use_move_ordering": True,
#                         "parameters": {
#                             "use_killer_moves": True,
#                             "use_history_heuristic": True
#                         }
#                     },
#                     {
#                         "algorithm_type": "alphabeta", 
#                         "name": "AlphaBeta-Limited-5",
#                         "description": "Alpha-beta with depth limit 5",
#                         "depth_limit": 5,
#                         "use_move_ordering": True
#                     },
#                     {
#                         "algorithm_type": "alphabeta",
#                         "name": "AlphaBeta-Limited-8", 
#                         "description": "Alpha-beta with depth limit 8",
#                         "depth_limit": 8,
#                         "use_move_ordering": True
#                     }
#                 ]
#             },
#             "heuristics": {
#                 "heuristics": [
#                     {
#                         "heuristic_type": "closeness",
#                         "name": "Closeness",
#                         "description": "Focuses on closeness to 21"
#                     },
#                     {
#                         "heuristic_type": "aggressive",
#                         "name": "Aggressive",
#                         "description": "Always goes for higher values"
#                     },
#                     {
#                         "heuristic_type": "cautious",
#                         "name": "Cautious",
#                         "description": "Strongly avoids busting"
#                     },
#                     {
#                         "heuristic_type": "balanced",
#                         "name": "Balanced",
#                         "description": "Balanced consideration of all factors"
#                     }
#                 ]
#             },
#             "stacks": {
#                 "stacks": [
#                     {
#                         "stack_type": "random",
#                         "length": 8,
#                         "name": "Random-8"
#                     },
#                     {
#                         "stack_type": "random",
#                         "length": 12,
#                         "name": "Random-12"
#                     },
#                     {
#                         "stack_type": "random",
#                         "length": 16,
#                         "name": "Random-16"
#                     },
#                     {
#                         "stack_type": "balanced",
#                         "length": 8,
#                         "name": "Balanced-8"
#                     },
#                     {
#                         "stack_type": "balanced",
#                         "length": 12,
#                         "name": "Balanced-12"
#                     },
#                     {
#                         "stack_type": "biased_high",
#                         "length": 10,
#                         "name": "BiasedHigh-10"
#                     },
#                     {
#                         "stack_type": "alternating",
#                         "length": 12,
#                         "name": "Alternating-12"
#                     }
#                 ]
#             },
#             "constraints": {
#                 "max_total_time_seconds": 3600,
#                 "max_time_per_experiment_seconds": 30,
#                 "max_parallel_workers": 4
#             },
#             "test_all_combinations": True,
#             "sample_experiments": False,
#             "output": {
#                 "output_base_dir": "comprehensive_benchmark_results"
#             }
#         }
    
#     def _create_algorithm_comparison_preset(self) -> Dict[str, Any]:
#         """Create algorithm comparison preset - COMPLETE VERSION"""
#     return {
#         "name": "Algorithm Comparison",
#         "description": "Compare Minimax vs Alpha-Beta with different configurations",
#         "algorithms": {
#             "algorithms": [
#                 {
#                     "algorithm_type": "minimax",
#                     "name": "Minimax-NoOpt",
#                     "description": "Minimax without optimizations",
#                     "depth_limit": None,
#                     "use_transposition_table": False,
#                     "use_move_ordering": False
#                 },
#                 {
#                     "algorithm_type": "minimax",
#                     "name": "Minimax-Transposition",
#                     "description": "Minimax with transposition table",
#                     "depth_limit": None,
#                     "use_transposition_table": True,
#                     "use_move_ordering": False
#                 },
#                 {
#                     "algorithm_type": "minimax",
#                     "name": "Minimax-MoveOrder",
#                     "description": "Minimax with move ordering",
#                     "depth_limit": None,
#                     "use_transposition_table": False,
#                     "use_move_ordering": True
#                 },
#                 {
#                     "algorithm_type": "minimax",
#                     "name": "Minimax-FullOpt",
#                     "description": "Minimax with all optimizations",
#                     "depth_limit": None,
#                     "use_transposition_table": True,
#                     "use_move_ordering": True
#                 },
#                 {
#                     "algorithm_type": "alphabeta",
#                     "name": "AlphaBeta-NoOpt",
#                     "description": "Alpha-beta without move ordering",
#                     "depth_limit": None,
#                     "use_move_ordering": False
#                 },
#                 {
#                     "algorithm_type": "alphabeta",
#                     "name": "AlphaBeta-MoveOrder",
#                     "description": "Alpha-beta with move ordering",
#                     "depth_limit": None,
#                     "use_move_ordering": True
#                 },
#                 {
#                     "algorithm_type": "alphabeta",
#                     "name": "AlphaBeta-Killer",
#                     "description": "Alpha-beta with killer moves",
#                     "depth_limit": None,
#                     "use_move_ordering": True,
#                     "parameters": {
#                         "use_killer_moves": True,
#                         "killer_move_depth": 2
#                     }
#                 }
#             ]
#         },
#         "heuristics": {
#             "heuristics": [
#                 {
#                     "heuristic_type": "balanced",
#                     "name": "Balanced",
#                     "description": "Balanced heuristic for fair comparison"
#                 }
#             ]
#         },
#         "stacks": {
#             "stacks": [
#                 {
#                     "stack_type": "random",
#                     "length": 6,
#                     "name": "Random-6",
#                     "description": "Random stack of length 6"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 8,
#                     "name": "Random-8",
#                     "description": "Random stack of length 8"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 10,
#                     "name": "Random-10",
#                     "description": "Random stack of length 10"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 12,
#                     "name": "Random-12",
#                     "description": "Random stack of length 12"
#                 }
#             ]
#         },
#         "constraints": {
#             "max_total_time_seconds": 1800,
#             "max_time_per_experiment_seconds": 60,
#             "max_parallel_workers": 4
#         },
#         "test_all_combinations": True,
#         "output": {
#             "output_base_dir": "algorithm_comparison_results",
#             "save_results": True,
#             "save_logs": True,
#             "generate_plots": True
#         }
#     }

# def _create_heuristic_analysis_preset(self) -> Dict[str, Any]:
#     """Create heuristic analysis preset - COMPLETE VERSION"""
#     return {
#         "name": "Heuristic Analysis",
#         "description": "Analyze effectiveness of different heuristics",
#         "algorithms": {
#             "algorithms": [
#                 {
#                     "algorithm_type": "alphabeta",
#                     "name": "AlphaBeta-Optimized",
#                     "description": "Alpha-beta with optimizations for fair heuristic comparison",
#                     "depth_limit": None,
#                     "use_move_ordering": True,
#                     "parameters": {
#                         "use_killer_moves": True,
#                         "use_history_heuristic": True
#                     }
#                 }
#             ]
#         },
#         "heuristics": {
#             "heuristics": [
#                 {
#                     "heuristic_type": "closeness",
#                     "name": "Closeness-Basic",
#                     "description": "Basic closeness heuristic"
#                 },
#                 {
#                     "heuristic_type": "closeness",
#                     "name": "Closeness-Weighted",
#                     "description": "Weighted closeness heuristic",
#                     "parameters": {
#                         "distance_weight": 75,
#                         "perfect_score_bonus": 1000
#                     }
#                 },
#                 {
#                     "heuristic_type": "aggressive",
#                     "name": "Aggressive-Basic",
#                     "description": "Basic aggressive heuristic"
#                 },
#                 {
#                     "heuristic_type": "aggressive",
#                     "name": "Aggressive-Risky",
#                     "description": "Highly aggressive heuristic",
#                     "parameters": {
#                         "bust_penalty": 20000,
#                         "aggression_factor": 0.9
#                     }
#                 },
#                 {
#                     "heuristic_type": "cautious",
#                     "name": "Cautious-Basic",
#                     "description": "Basic cautious heuristic"
#                 },
#                 {
#                     "heuristic_type": "cautious",
#                     "name": "Cautious-Extreme",
#                     "description": "Extremely cautious heuristic",
#                     "parameters": {
#                         "safety_margin": 5,
#                         "bust_penalty": 50000
#                     }
#                 },
#                 {
#                     "heuristic_type": "balanced",
#                     "name": "Balanced-Basic",
#                     "description": "Basic balanced heuristic"
#                 },
#                 {
#                     "heuristic_type": "balanced",
#                     "name": "Balanced-Aggressive",
#                     "description": "Balanced heuristic leaning aggressive",
#                     "weights": {
#                         "closeness": 0.3,
#                         "safety": 0.2,
#                         "aggression": 0.4,
#                         "flexibility": 0.1
#                     }
#                 },
#                 {
#                     "heuristic_type": "balanced",
#                     "name": "Balanced-Cautious",
#                     "description": "Balanced heuristic leaning cautious",
#                     "weights": {
#                         "closeness": 0.3,
#                         "safety": 0.5,
#                         "aggression": 0.1,
#                         "flexibility": 0.1
#                     }
#                 }
#             ]
#         },
#         "stacks": {
#             "stacks": [
#                 {
#                     "stack_type": "random",
#                     "length": 8,
#                     "name": "Random-8",
#                     "description": "Random stack for heuristic testing"
#                 },
#                 {
#                     "stack_type": "balanced",
#                     "length": 8,
#                     "name": "Balanced-8",
#                     "description": "Balanced stack for heuristic testing"
#                 },
#                 {
#                     "stack_type": "biased_high",
#                     "length": 8,
#                     "name": "BiasedHigh-8",
#                     "description": "High-value biased stack"
#                 },
#                 {
#                     "stack_type": "alternating",
#                     "length": 8,
#                     "name": "Alternating-8",
#                     "description": "Alternating high-low stack"
#                 }
#             ]
#         },
#         "constraints": {
#             "max_total_time_seconds": 1200,
#             "max_time_per_experiment_seconds": 30,
#             "max_parallel_workers": 4
#         },
#         "test_all_combinations": True,
#         "output": {
#             "output_base_dir": "heuristic_analysis_results",
#             "save_results": True,
#             "save_logs": True,
#             "generate_plots": True,
#             "plot_types": ["heuristic_comparison", "performance_by_stack"]
#         }
#     }

# def _create_scalability_study_preset(self) -> Dict[str, Any]:
#     """Create scalability study preset - COMPLETE VERSION"""
#     return {
#         "name": "Scalability Study",
#         "description": "Study algorithm scalability with increasing stack size",
#         "algorithms": {
#             "algorithms": [
#                 {
#                     "algorithm_type": "minimax",
#                     "name": "Minimax",
#                     "description": "Standard Minimax algorithm",
#                     "depth_limit": None,
#                     "use_transposition_table": False,
#                     "use_move_ordering": False
#                 },
#                 {
#                     "algorithm_type": "alphabeta",
#                     "name": "AlphaBeta",
#                     "description": "Alpha-Beta pruning",
#                     "depth_limit": None,
#                     "use_move_ordering": True
#                 },
#                 {
#                     "algorithm_type": "alphabeta",
#                     "name": "AlphaBeta-Depth5",
#                     "description": "Alpha-Beta with depth limit 5",
#                     "depth_limit": 5,
#                     "use_move_ordering": True
#                 },
#                 {
#                     "algorithm_type": "alphabeta",
#                     "name": "AlphaBeta-Depth8",
#                     "description": "Alpha-Beta with depth limit 8",
#                     "depth_limit": 8,
#                     "use_move_ordering": True
#                 }
#             ]
#         },
#         "heuristics": {
#             "heuristics": [
#                 {
#                     "heuristic_type": "balanced",
#                     "name": "Balanced",
#                     "description": "Balanced heuristic for scalability testing"
#                 }
#             ]
#         },
#         "stacks": {
#             "stacks": [
#                 {
#                     "stack_type": "random",
#                     "length": 4,
#                     "name": "Random-4",
#                     "description": "Small random stack"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 6,
#                     "name": "Random-6",
#                     "description": "Medium-small random stack"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 8,
#                     "name": "Random-8",
#                     "description": "Medium random stack"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 10,
#                     "name": "Random-10",
#                     "description": "Medium-large random stack"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 12,
#                     "name": "Random-12",
#                     "description": "Large random stack"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 14,
#                     "name": "Random-14",
#                     "description": "Very large random stack"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 16,
#                     "name": "Random-16",
#                     "description": "Extra large random stack"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 18,
#                     "name": "Random-18",
#                     "description": "Massive random stack"
#                 },
#                 {
#                     "stack_type": "random",
#                     "length": 20,
#                     "name": "Random-20",
#                     "description": "Maximum test random stack"
#                 }
#             ]
#         },
#         "constraints": {
#             "max_total_time_seconds": 3600,
#             "max_time_per_experiment_seconds": 120,
#             "max_parallel_workers": 4,
#             "timeout_behavior": "skip"
#         },
#         "test_all_combinations": True,
#         "output": {
#             "output_base_dir": "scalability_study_results",
#             "save_results": True,
#             "save_logs": True,
#             "generate_plots": True,
#             "plot_types": ["scalability_curves", "time_complexity"]
#         },
#         "metrics": {
#             "track_memory": True,
#             "track_time": True,
#             "track_node_count": True,
#             "track_cache_hits": True
#         }
#     }
    
#     def get_preset_names(self) -> List[str]:
#         """Get list of available preset names"""
#         return list(self.presets.keys())
    
#     def load_preset(self, preset_name: str) -> ExperimentConfig:
#         """Load a preset configuration"""
#         if preset_name not in self.presets:
#             available = ", ".join(self.get_preset_names())
#             raise ValueError(f"Unknown preset: {preset_name}. Available: {available}")
        
#         preset_data = self.presets[preset_name]
#         return self.create_config_from_dict(preset_data)
    
#     def create_config_from_dict(self, config_dict: Dict[str, Any]) -> ExperimentConfig:
#         """Create ExperimentConfig from dictionary"""
#         # Deep copy to avoid modifying preset
#         config_dict = copy.deepcopy(config_dict)
        
#         # Convert nested configurations
#         if "algorithms" in config_dict:
#             if isinstance(config_dict["algorithms"], dict):
#                 config_dict["algorithms"] = AlgorithmSuiteConfig.from_dict(
#                     config_dict["algorithms"]
#                 )
        
#         if "heuristics" in config_dict:
#             if isinstance(config_dict["heuristics"], dict):
#                 config_dict["heuristics"] = HeuristicSuiteConfig.from_dict(
#                     config_dict["heuristics"]
#                 )
        
#         if "stacks" in config_dict:
#             if isinstance(config_dict["stacks"], dict):
#                 config_dict["stacks"] = StackSuiteConfig.from_dict(
#                     config_dict["stacks"]
#                 )
        
#         if "constraints" in config_dict:
#             from .experiment_config import ExperimentConstraints
#             if isinstance(config_dict["constraints"], dict):
#                 config_dict["constraints"] = ExperimentConstraints.from_dict(
#                     config_dict["constraints"]
#                 )
        
#         if "metrics" in config_dict:
#             from .experiment_config import ExperimentMetrics
#             if isinstance(config_dict["metrics"], dict):
#                 config_dict["metrics"] = ExperimentMetrics.from_dict(
#                     config_dict["metrics"]
#                 )
        
#         if "output" in config_dict:
#             from .experiment_config import ExperimentOutput
#             if isinstance(config_dict["output"], dict):
#                 config_dict["output"] = ExperimentOutput.from_dict(
#                     config_dict["output"]
#                 )
        
#         return ExperimentConfig.from_dict(config_dict)
    
#     def save_config(self, config: ExperimentConfig, filename: str):
#         """Save configuration to file"""
#         filepath = self.config_dir / filename
        
#         # Ensure directory exists
#         filepath.parent.mkdir(exist_ok=True, parents=True)
        
#         # Save based on file extension
#         if filepath.suffix.lower() == '.json':
#             config.to_json(str(filepath))
#         elif filepath.suffix.lower() in ['.yaml', '.yml']:
#             config.to_yaml(str(filepath))
#         else:
#             # Default to JSON
#             filepath = filepath.with_suffix('.json')
#             config.to_json(str(filepath))
    
#     def load_config(self, filename: str) -> ExperimentConfig:
#         """Load configuration from file"""
#         filepath = self.config_dir / filename
        
#         if not filepath.exists():
#             raise FileNotFoundError(f"Config file not found: {filepath}")
        
#         if filepath.suffix.lower() == '.json':
#             return ExperimentConfig.from_json(str(filepath))
#         elif filepath.suffix.lower() in ['.yaml', '.yml']:
#             return ExperimentConfig.from_yaml(str(filepath))
#         else:
#             raise ValueError(f"Unsupported file format: {filepath.suffix}")
    
#     def create_custom_config(self, **kwargs) -> ExperimentConfig:
#         """Create custom configuration with overrides"""
#         # Start with default config
#         config = ExperimentConfig()
        
#         # Apply overrides
#         for key, value in kwargs.items():
#             if hasattr(config, key):
#                 setattr(config, key, value)
#             else:
#                 # Try to set nested attributes
#                 parts = key.split('.')
#                 obj = config
#                 for part in parts[:-1]:
#                     if hasattr(obj, part):
#                         obj = getattr(obj, part)
#                     else:
#                         raise AttributeError(f"Invalid config attribute: {key}")
                
#                 if hasattr(obj, parts[-1]):
#                     setattr(obj, parts[-1], value)
#                 else:
#                     raise AttributeError(f"Invalid config attribute: {key}")
        
#         return config
    
#     def validate_config(self, config: ExperimentConfig) -> Dict[str, Any]:
#         """Validate configuration and return validation results"""
#         errors = config.validate()
        
#         return {
#             "is_valid": len(errors) == 0,
#             "errors": errors,
#             "summary": config.get_config_summary(),
#             "total_experiments": config.get_total_experiments(),
#             "estimated_time": self._estimate_total_time(config)
#         }
    
#     def _estimate_total_time(self, config: ExperimentConfig) -> Dict[str, float]:
#         """Estimate total execution time"""
#         total_experiments = config.get_total_experiments()
        
#         # Rough estimation: 0.1s per experiment per 10 stack values
#         avg_stack_length = config.stacks.statistics.get("avg_stack_length", 10)
#         time_per_experiment = 0.1 * (avg_stack_length / 10)
        
#         total_sequential = total_experiments * time_per_experiment
#         total_parallel = total_sequential / config.constraints.max_parallel_workers
        
#         return {
#             "experiments_per_second": 1 / time_per_experiment,
#             "time_per_experiment_seconds": time_per_experiment,
#             "total_sequential_seconds": total_sequential,
#             "total_parallel_seconds": total_parallel,
#             "total_sequential_minutes": total_sequential / 60,
#             "total_parallel_minutes": total_parallel / 60
#         }
    
#     def generate_config_report(self, config: ExperimentConfig) -> str:
#         """Generate human-readable configuration report"""
#         validation = self.validate_config(config)
        
#         report_lines = [
#             "=" * 80,
#             f"EXPERIMENT CONFIGURATION REPORT: {config.name}",
#             "=" * 80,
#             f"Description: {config.description}",
#             f"Experiment ID: {config.get_experiment_id()}",
#             f"Timestamp: {config.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
#             "",
#             "VALIDATION:",
#             f"  Status: {'VALID' if validation['is_valid'] else 'INVALID'}",
#             ""
#         ]
        
#         if validation['errors']:
#             report_lines.append("  Errors:")
#             for error in validation['errors']:
#                 report_lines.append(f"    - {error}")
#             report_lines.append("")
        
#         summary = validation['summary']
#         report_lines.extend([
#             "CONFIGURATION SUMMARY:",
#             f"  Algorithms: {summary['total_algorithms']}",
#             f"  Heuristics: {summary['total_heuristics']}",
#             f"  Stacks: {summary['total_stacks']}",
#             f"  Total Experiments: {summary['total_experiments']}",
#             "",
#             "ALGORITHM TYPES:",
#         ])
        
#         for algo_type in summary['algorithm_types']:
#             count = len([
#                 a for a in config.algorithms.algorithms 
#                 if a.algorithm_type.value == algo_type
#             ])
#             report_lines.append(f"  - {algo_type}: {count} algorithms")
        
#         report_lines.extend([
#             "",
#             "STACK STATISTICS:",
#             f"  Min Length: {min(s.length for s in config.stacks.stacks)}",
#             f"  Max Length: {max(s.length for s in config.stacks.stacks)}",
#             f"  Avg Length: {summary['stack_lengths']}",
#             "",
#             "CONSTRAINTS:",
#             f"  Max Total Time: {summary['constraints']['max_total_time']}s",
#             f"  Max Time per Experiment: {summary['constraints']['max_time_per_experiment']}s",
#             f"  Max Parallel Workers: {summary['constraints']['max_parallel_workers']}",
#             "",
#             "TIME ESTIMATION:",
#             f"  Time per Experiment: {validation['estimated_time']['time_per_experiment_seconds']:.3f}s",
#             f"  Experiments per Second: {validation['estimated_time']['experiments_per_second']:.1f}",
#             f"  Total Sequential Time: {validation['estimated_time']['total_sequential_minutes']:.1f} minutes",
#             f"  Total Parallel Time: {validation['estimated_time']['total_parallel_minutes']:.1f} minutes",
#             "",
#             "OUTPUT:",
#             f"  Results Directory: {config.output.output_base_dir}",
#             f"  Database: {config.output.database_path if config.output.use_database else 'None'}",
#             "=" * 80
#         ])
        
#         return "\n".join(report_lines)
