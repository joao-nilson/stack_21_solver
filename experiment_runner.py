#!/usr/bin/env python3
"""
Integrated Experiment Runner for Stack-based 21 Solver
Uses Unified Configuration Management to run comprehensive experiments
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import traceback

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config_manager import ConfigManager
from config.experiment_config import ExperimentConfig
from src.game.game_state import GameState
from src.algorithms.minimax import MinimaxSolver
from src.algorithms.alphabeta import AlphaBetaSolver
from src.utils.logger import GameLogger
from src.utils.performance import PerformanceMonitor


class ExperimentRunner:
    """Main experiment runner that uses configuration system"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.experiment_id = config.get_experiment_id()
        self.logger = GameLogger(
            name=f"ExperimentRunner-{self.experiment_id}",
            log_level="INFO" if config.validate_before_run else "DEBUG"
        )
        self.results = []
        self.metrics = {}
        self.start_time = None
        self.output_paths = config.output.get_output_paths()
        
        # Setup output directories
        for key, path in self.output_paths.items():
            if key not in ["base", "timestamp"]:
                Path(path).mkdir(parents=True, exist_ok=True)
        
        self.logger.logger.info(f"Initialized Experiment Runner with ID: {self.experiment_id}")
        self.logger.logger.info(f"Output directory: {self.output_paths['results']}")
    
    def validate_configuration(self) -> bool:
        """Validate experiment configuration before running"""
        self.logger.logger.info("Validating configuration...")
        
        errors = self.config.validate()
        
        if errors:
            self.logger.logger.error("Configuration validation failed:")
            for error in errors:
                self.logger.logger.error(f"  - {error}")
            return False
        
        self.logger.logger.info("✓ Configuration is valid")
        
        # Log configuration summary
        summary = self.config.get_config_summary()
        self.logger.logger.info(f"Total experiments to run: {summary['total_experiments']}")
        self.logger.logger.info(f"Algorithms: {summary['total_algorithms']}")
        self.logger.logger.info(f"Heuristics: {summary['total_heuristics']}")
        self.logger.logger.info(f"Stacks: {summary['total_stacks']}")
        
        return True
    
    def get_heuristic_function(self, heuristic_config):
        """Get heuristic function from configuration"""
        from examples.heuristic_analysis import HeuristicAnalysis
        from examples.solution_path_demo import SolutionPathDemo
        
        # Map heuristic types to functions
        heuristic_analysis = HeuristicAnalysis()
        solution_demo = SolutionPathDemo()
        
        # Define heuristic families from heuristic_analysis
        heuristic_analysis.define_heuristic_families()
        
        # Get heuristics from solution_path_demo
        solution_demo.define_heuristics()
        
        # Map heuristic type to actual function
        heuristic_map = {
            "closeness": solution_demo.heuristics.get("closeness"),
            "aggressive": solution_demo.heuristics.get("aggressive"),
            "cautious": solution_demo.heuristics.get("cautious"),
            "balanced": solution_demo.heuristics.get("balanced")
        }
        
        heuristic_func = heuristic_map.get(heuristic_config.heuristic_type.value)
        
        if not heuristic_func:
            # Fallback to default heuristic
            self.logger.logger.warning(f"Heuristic {heuristic_config.heuristic_type} not found, using default")
            return solution_demo.heuristics.get("closeness")
        
        return heuristic_func
    
    def create_game_state(self, stack: List[int], heuristic_func) -> GameState:
        """Create game state with custom heuristic"""
        class ConfiguredGameState(GameState):
            def evaluate(self):
                return heuristic_func(self)
        
        return ConfiguredGameState(
            total=0,
            stack_index=0,
            stack=stack,
            is_maximizing=True
        )
    
    def run_single_experiment(self, combination: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single experiment with given combination"""
        experiment_start = time.time()
        
        algorithm_config = combination["algorithm"]
        heuristic_config = combination["heuristic"]
        stack_config = combination["stack"]
        
        self.logger.logger.info(f"Running experiment: {combination['combination_id']}")
        
        # Generate stack
        stack = stack_config.generate_stack()
        
        # Get heuristic function
        heuristic_func = self.get_heuristic_function(heuristic_config)
        
        # Create game state
        initial_state = self.create_game_state(stack, heuristic_func)
        
        # Create solver based on algorithm configuration
        if algorithm_config.algorithm_type.value == "minimax":
            solver = MinimaxSolver(depth_limit=algorithm_config.depth_limit)
            algorithm_name = "minimax"
        else:  # alphabeta
            solver = AlphaBetaSolver(depth_limit=algorithm_config.depth_limit)
            algorithm_name = "alphabeta"
        
        # Run algorithm with performance monitoring
        performance = PerformanceMonitor(enabled=True)
        performance.start()
        
        try:
            if algorithm_name == "minimax":
                value, best_child = solver.solve(initial_state)
                path = solver.find_optimal_path(initial_state)
                terminal_state = path[-1] if path else None
            else:  # alphabeta
                value, terminal_state = solver.solve(initial_state)
                path = solver.get_solution_path(initial_state)
            
            performance.stop()
            
            # Get statistics
            stats = solver.get_statistics()
            perf_stats = performance.get_current_stats()
            
            # Combine stats
            combined_stats = {**stats, **perf_stats}
            
            # Calculate game metrics
            game_metrics = self.calculate_game_metrics(path, terminal_state)
            
            # Build result
            result = {
                "experiment_id": combination["combination_id"],
                "timestamp": datetime.now().isoformat(),
                "algorithm": algorithm_config.name,
                "algorithm_type": algorithm_config.algorithm_type.value,
                "heuristic": heuristic_config.name,
                "heuristic_type": heuristic_config.heuristic_type.value,
                "stack": stack_config.name,
                "stack_type": stack_config.stack_type.value,
                "stack_length": stack_config.length,
                "stack_values": stack,
                "algorithm_parameters": algorithm_config.parameters,
                "heuristic_parameters": heuristic_config.parameters,
                "value": value,
                "execution_time": time.time() - experiment_start,
                "statistics": combined_stats,
                "game_metrics": game_metrics,
                "path_length": len(path) if path else 0,
                "final_total": terminal_state.total if terminal_state else None,
                "is_21": terminal_state.total == 21 if terminal_state else False,
                "is_bust": terminal_state.total > 21 if terminal_state else False
            }
            
            # Add performance stats
            for key, value in perf_stats.items():
                result[f"performance_{key}"] = value
            
            self.logger.logger.info(
                f"✓ Experiment completed: {combination['combination_id']} "
                f"Value: {result['value']:.1f}, "
                f"Time: {result['execution_time']:.3f}s, "
                f"Final: {result['final_total']}"
            )
            
            return result
            
        except Exception as e:
            performance.stop()
            self.logger.logger.error(f"Experiment failed: {combination['combination_id']} - {e}")
            
            return {
                "experiment_id": combination["combination_id"],
                "timestamp": datetime.now().isoformat(),
                "algorithm": algorithm_config.name,
                "heuristic": heuristic_config.name,
                "stack": stack_config.name,
                "error": str(e),
                "error_traceback": traceback.format_exc(),
                "execution_time": time.time() - experiment_start
            }
    
    def calculate_game_metrics(self, path: List[GameState], terminal_state: GameState) -> Dict[str, Any]:
        """Calculate game-specific metrics from solution path"""
        if not path or not terminal_state:
            return {}
        
        # Extract move values
        moves_taken = []
        moves_discarded = []
        
        for state in path[1:]:
            if state.move_from_parent:
                moves_taken.append(state.move_from_parent[0])
                moves_discarded.append(state.move_from_parent[1])
        
        # Calculate metrics
        metrics = {
            "moves_count": len(moves_taken),
            "final_total": terminal_state.total,
            "distance_from_21": abs(21 - terminal_state.total),
            "is_win": terminal_state.total == 21,
            "is_bust": terminal_state.total > 21,
            "avg_move_value": sum(moves_taken) / len(moves_taken) if moves_taken else 0,
            "max_move_value": max(moves_taken) if moves_taken else 0,
            "min_move_value": min(moves_taken) if moves_taken else 0,
            "total_value_taken": sum(moves_taken),
            "total_value_discarded": sum(moves_discarded),
            "game_completion": (terminal_state.stack_index / len(terminal_state.stack)) * 100
            if hasattr(terminal_state, 'stack') and terminal_state.stack else 0
        }
        
        return metrics
    
    def run_experiments(self) -> List[Dict[str, Any]]:
        """Run all experiments defined in configuration"""
        self.start_time = time.time()
        
        # Validate configuration first
        if self.config.validate_before_run:
            if not self.validate_configuration():
                self.logger.logger.error("Configuration validation failed. Aborting.")
                return []
        
        # Get all experiment combinations
        combinations = self.config.get_experiment_combinations()
        
        if not combinations:
            self.logger.logger.error("No experiment combinations to run")
            return []
        
        self.logger.logger.info(f"Starting {len(combinations)} experiments...")
        
        # Check constraints
        if self.config.constraints.max_total_time_seconds:
            estimated_time = len(combinations) * (self.config.constraints.max_time_per_experiment_seconds or 60)
            if estimated_time > self.config.constraints.max_total_time_seconds:
                self.logger.logger.warning(
                    f"Estimated time ({estimated_time:.0f}s) exceeds max total time "
                    f"({self.config.constraints.max_total_time_seconds}s)"
                )
        
        # Run experiments
        results = []
        completed = 0
        errors = 0
        
        for i, combination in enumerate(combinations, 1):
            # Check time constraint
            if self.config.constraints.max_total_time_seconds:
                elapsed = time.time() - self.start_time
                if elapsed > self.config.constraints.max_total_time_seconds:
                    self.logger.logger.warning(
                        f"Time limit exceeded ({elapsed:.0f}s > "
                        f"{self.config.constraints.max_total_time_seconds}s). Stopping."
                    )
                    break
            
            self.logger.logger.info(f"Progress: {i}/{len(combinations)} ({i/len(combinations)*100:.1f}%)")
            
            # Run experiment
            result = self.run_single_experiment(combination)
            
            if "error" in result:
                errors += 1
            else:
                completed += 1
            
            results.append(result)
            
            # Save intermediate results periodically
            if i % 10 == 0:
                self.save_intermediate_results(results)
        
        # Final save
        self.results = results
        self.save_results()
        
        # Generate summary
        self.generate_summary(completed, errors)
        
        return results
    
    def save_intermediate_results(self, results: List[Dict[str, Any]]):
        """Save intermediate results during experiment run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"intermediate_results_{timestamp}.json"
        filepath = Path(self.output_paths["results"]) / filename
        
        # Save raw results
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save aggregated summary
        self.save_aggregated_summary(results)
    
    def save_results(self):
        """Save all experiment results"""
        results_file = Path(self.output_paths["results"]) / "experiment_results.json"
        
        # Clean results for JSON serialization
        cleaned_results = []
        for result in self.results:
            cleaned = {}
            for key, value in result.items():
                if hasattr(value, '__dict__'):
                    # Convert objects to dict
                    cleaned[key] = self._clean_for_json(value.__dict__)
                else:
                    cleaned[key] = self._clean_for_json(value)
            cleaned_results.append(cleaned)
        
        # Save raw results
        with open(results_file, 'w') as f:
            json.dump(cleaned_results, f, indent=2, default=str)
        
        self.logger.logger.info(f"Results saved to: {results_file}")
        
        # Save aggregated results
        self.save_aggregated_results()
        
        # Save configuration
        config_file = Path(self.output_paths["results"]) / "experiment_config.json"
        self.config.to_json(str(config_file))
        
        # Generate reports
        self.generate_reports()
    
    def _clean_for_json(self, obj):
        """Clean object for JSON export"""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, dict):
            return {key: self._clean_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # Convert objects to dict
            return self._clean_for_json(obj.__dict__)
        else:
            return str(obj)
    
    def save_aggregated_results(self):
        """Save aggregated results summary"""
        if not self.results:
            return
        
        # Aggregate successful results
        successful_results = [r for r in self.results if "error" not in r]
        
        if not successful_results:
            return
        
        # Calculate aggregates by algorithm
        aggregates = {}
        
        for result in successful_results:
            algo_key = result["algorithm"]
            heuristic_key = result["heuristic"]
            stack_type_key = result["stack_type"]
            
            if algo_key not in aggregates:
                aggregates[algo_key] = {
                    "algorithm": algo_key,
                    "count": 0,
                    "total_value": 0,
                    "total_time": 0,
                    "total_nodes": 0,
                    "wins": 0,
                    "busts": 0,
                    "final_totals": [],
                    "execution_times": [],
                    "by_heuristic": {},
                    "by_stack_type": {}
                }
            
            agg = aggregates[algo_key]
            agg["count"] += 1
            agg["total_value"] += result.get("value", 0)
            agg["total_time"] += result.get("execution_time", 0)
            agg["total_nodes"] += result.get("statistics", {}).get("nodes_evaluated", 0)
            
            if result.get("is_21"):
                agg["wins"] += 1
            if result.get("is_bust"):
                agg["busts"] += 1
            
            agg["final_totals"].append(result.get("final_total", 0))
            agg["execution_times"].append(result.get("execution_time", 0))
            
            # Aggregate by heuristic
            if heuristic_key not in agg["by_heuristic"]:
                agg["by_heuristic"][heuristic_key] = {
                    "count": 0,
                    "avg_value": 0,
                    "win_rate": 0
                }
            heur_agg = agg["by_heuristic"][heuristic_key]
            heur_agg["count"] += 1
        
        # Calculate averages
        for algo_key, agg in aggregates.items():
            agg["avg_value"] = agg["total_value"] / agg["count"] if agg["count"] > 0 else 0
            agg["avg_time"] = agg["total_time"] / agg["count"] if agg["count"] > 0 else 0
            agg["avg_nodes"] = agg["total_nodes"] / agg["count"] if agg["count"] > 0 else 0
            agg["win_rate"] = agg["wins"] / agg["count"] if agg["count"] > 0 else 0
            agg["bust_rate"] = agg["busts"] / agg["count"] if agg["count"] > 0 else 0
            agg["avg_final_total"] = sum(agg["final_totals"]) / len(agg["final_totals"]) if agg["final_totals"] else 0
        
        # Save aggregates
        aggregates_file = Path(self.output_paths["results"]) / "aggregated_results.json"
        with open(aggregates_file, 'w') as f:
            json.dump(aggregates, f, indent=2, default=str)
        
        self.logger.logger.info(f"Aggregated results saved to: {aggregates_file}")
    
    def save_aggregated_summary(self, results: List[Dict[str, Any]]):
        """Save a quick summary of current progress"""
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_experiments": len(results),
            "completed": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "avg_execution_time": sum(r.get("execution_time", 0) for r in successful) / len(successful) if successful else 0,
            "total_time_elapsed": time.time() - self.start_time
        }
        
        summary_file = Path(self.output_paths["results"]) / "progress_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def generate_summary(self, completed: int, errors: int):
        """Generate experiment summary"""
        total_time = time.time() - self.start_time
        
        summary_lines = [
            "=" * 80,
            "EXPERIMENT SUMMARY",
            "=" * 80,
            f"Experiment ID: {self.experiment_id}",
            f"Total experiments: {len(self.results)}",
            f"Completed: {completed}",
            f"Failed: {errors}",
            f"Success rate: {completed/len(self.results)*100:.1f}%" if self.results else "0%",
            f"Total time: {total_time:.2f}s",
            f"Avg time per experiment: {total_time/len(self.results):.2f}s" if self.results else "N/A",
            "",
            "Output files:",
            f"  • Results: {self.output_paths['results']}/experiment_results.json",
            f"  • Aggregated: {self.output_paths['results']}/aggregated_results.json",
            f"  • Configuration: {self.output_paths['results']}/experiment_config.json",
            f"  • Logs: {self.output_paths['logs']}",
            "=" * 80
        ]
        
        summary_text = "\n".join(summary_lines)
        
        # Print to console
        print(summary_text)
        
        # Save to file
        summary_file = Path(self.output_paths["results"]) / "experiment_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(summary_text)
        
        self.logger.logger.info(f"Experiment summary saved to: {summary_file}")
    
    def generate_reports(self):
        """Generate detailed reports and visualizations"""
        # This can be expanded to generate charts, HTML reports, etc.
        # For now, we'll just create a simple markdown report
        
        report_lines = [
            "# Experiment Report",
            f"**Experiment ID**: {self.experiment_id}",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Configuration**: {self.config.name}",
            "",
            "## Configuration Summary",
            f"- Algorithms: {len(self.config.algorithms.algorithms)}",
            f"- Heuristics: {len(self.config.heuristics.heuristics)}",
            f"- Stacks: {len(self.config.stacks.stacks)}",
            f"- Total experiments: {self.config.get_total_experiments()}",
            "",
            "## Results Summary",
            f"- Completed: {len([r for r in self.results if 'error' not in r])}",
            f"- Failed: {len([r for r in self.results if 'error' in r])}",
        ]
        
        # Add algorithm performance
        report_lines.extend(["", "## Algorithm Performance"])
        
        # Group by algorithm
        algo_results = {}
        for result in self.results:
            if "error" in result:
                continue
            algo = result["algorithm"]
            if algo not in algo_results:
                algo_results[algo] = []
            algo_results[algo].append(result)
        
        for algo, results_list in algo_results.items():
            avg_time = sum(r["execution_time"] for r in results_list) / len(results_list)
            avg_value = sum(r["value"] for r in results_list) / len(results_list)
            wins = sum(1 for r in results_list if r.get("is_21", False))
            
            report_lines.append(
                f"- **{algo}**: {len(results_list)} runs, "
                f"Avg time: {avg_time:.3f}s, "
                f"Avg value: {avg_value:.1f}, "
                f"Wins: {wins} ({wins/len(results_list)*100:.1f}%)"
            )
        
        # Save report
        report_file = Path(self.output_paths["reports"]) / "experiment_report.md"
        with open(report_file, 'w') as f:
            f.write("\n".join(report_lines))
        
        self.logger.logger.info(f"Report generated: {report_file}")


def run_experiment_from_config(config_file: str = None, preset_name: str = None):
    """Run experiment from configuration file or preset"""
    manager = ConfigManager()
    
    if config_file:
        print(f"Loading configuration from: {config_file}")
        config = manager.load_config(config_file)
    elif preset_name:
        print(f"Loading preset: {preset_name}")
        config = manager.load_preset(preset_name)
    else:
        print("No configuration specified. Using quick_test preset.")
        config = manager.load_preset("quick_test")
    
    # Generate configuration report
    report = manager.generate_config_report(config)
    print(report)
    
    # Create and run experiment runner
    runner = ExperimentRunner(config)
    results = runner.run_experiments()
    
    return results


def main():
    """Main entry point for experiment runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Stack-based 21 experiments with unified configuration")
    parser.add_argument("--preset", type=str, choices=["quick_test", "comprehensive_benchmark", 
                                                      "algorithm_comparison", "heuristic_analysis", 
                                                      "scalability_study"],
                       help="Use a preset configuration")
    parser.add_argument("--config", type=str, help="Path to custom configuration file")
    parser.add_argument("--list-presets", action="store_true", help="List available presets")
    
    args = parser.parse_args()
    
    if args.list_presets:
        manager = ConfigManager()
        presets = manager.get_preset_names()
        print("Available presets:")
        for preset in presets:
            print(f"  - {preset}")
        return
    
    try:
        results = run_experiment_from_config(args.config, args.preset)
        
        if results:
            print(f"\nExperiment completed successfully!")
            print(f"Results saved to: experiment_results/{results[0].get('experiment_id', 'unknown')}")
        
    except Exception as e:
        print(f"Error running experiment: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
