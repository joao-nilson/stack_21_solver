"""
Statistical Aggregator for multi-run analysis across similar configurations
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import scipy.stats as stats  # For confidence intervals


class StatisticalAggregator:
    """
    Aggregates results across multiple experiment runs with similar configurations
    """
    
    def __init__(self, results_base_dir: str = "experiment_results/results"):
        self.results_base_dir = Path(results_base_dir)
        self.runs = []
        self.aggregated_groups = {}
        self.multi_run_stats = {}
    
    def discover_runs(self, pattern: str = "*") -> List[Path]:
        """
        Discover all experiment runs in the results directory
        
        Args:
            pattern: Glob pattern to match run directories
            
        Returns:
            List of Path objects for run directories
        """
        if not self.results_base_dir.exists():
            return []
        
        run_dirs = sorted(self.results_base_dir.glob(pattern))
        return [d for d in run_dirs if d.is_dir()]
    
    def load_run(self, run_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Load a single experiment run
        
        Args:
            run_dir: Path to run directory
            
        Returns:
            Dictionary with run data or None if loading fails
        """
        try:
            # Load aggregated results
            aggregated_file = run_dir / "aggregated_results.json"
            if not aggregated_file.exists():
                return None
            
            with open(aggregated_file, 'r') as f:
                aggregated_data = json.load(f)
            
            # Load experiment config
            config_file = run_dir / "experiment_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            else:
                config_data = {}
            
            # Load raw results if available
            results_file = run_dir / "experiment_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    raw_results = json.load(f)
            else:
                raw_results = []
            
            run_info = {
                "run_dir": str(run_dir),
                "timestamp": run_dir.name,
                "aggregated_data": aggregated_data,
                "config": config_data,
                "raw_results": raw_results,
                "metadata": {
                    "loaded_at": datetime.now().isoformat(),
                    "algorithm_count": len(aggregated_data),
                    "experiment_count": len(raw_results)
                }
            }
            
            return run_info
            
        except Exception as e:
            print(f"Error loading run {run_dir}: {e}")
            return None
    
    def load_all_runs(self, pattern: str = "*") -> Dict[str, List[Dict]]:
        """
        Load all runs and group by configuration similarity
        
        Args:
            pattern: Glob pattern for run directories
            
        Returns:
            Dictionary of grouped runs by configuration signature
        """
        run_dirs = self.discover_runs(pattern)
        all_runs = []
        
        print(f"Found {len(run_dirs)} run directories")
        
        # Load each run
        for run_dir in run_dirs:
            run_data = self.load_run(run_dir)
            if run_data:
                all_runs.append(run_data)
        
        # Group runs by configuration similarity
        grouped_runs = self._group_by_configuration(all_runs)
        
        # Calculate statistics for each group
        self.multi_run_stats = self._calculate_multi_run_statistics(grouped_runs)
        
        self.runs = all_runs
        self.aggregated_groups = grouped_runs
        
        return grouped_runs
    
    def _group_by_configuration(self, runs: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group runs by similar configurations
        
        Groups are determined by:
        1. Same algorithm names
        2. Same heuristic names  
        3. Similar stack configurations (type and length)
        
        Args:
            runs: List of loaded run data
            
        Returns:
            Dictionary mapping group keys to lists of runs
        """
        groups = {}
        
        for run in runs:
            # Create a configuration signature for grouping
            config = run.get("config", {})
            algorithms = config.get("algorithms", {}).get("algorithms", [])
            heuristics = config.get("heuristics", {}).get("heuristics", [])
            stacks = config.get("stacks", {}).get("stacks", [])
            
            # Extract algorithm names
            algo_names = sorted([algo.get("name", "") for algo in algorithms])
            
            # Extract heuristic names
            heuristic_names = sorted([heur.get("name", "") for heur in heuristics])
            
            # Extract stack characteristics
            stack_types = sorted([stack.get("stack_type", "") for stack in stacks])
            stack_lengths = sorted([stack.get("length", 0) for stack in stacks])
            
            # Create group key
            group_key = (
                "_".join(algo_names),
                "_".join(heuristic_names),
                "_".join(stack_types),
                "_".join(str(l) for l in stack_lengths)
            )
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(run)
        
        # Create human-readable group names
        named_groups = {}
        for i, (key, group_runs) in enumerate(groups.items()):
            if group_runs:
                first_run = group_runs[0]
                config = first_run.get("config", {})
                group_name = config.get("name", f"Group_{i+1}")
                
                # Count algorithms and heuristics
                algo_count = len(config.get("algorithms", {}).get("algorithms", []))
                heuristic_count = len(config.get("heuristics", {}).get("heuristics", []))
                stack_count = len(config.get("stacks", {}).get("stacks", []))
                
                named_groups[group_name] = {
                    "group_key": key,
                    "runs": group_runs,
                    "run_count": len(group_runs),
                    "config_summary": {
                        "algorithms": algo_count,
                        "heuristics": heuristic_count,
                        "stacks": stack_count,
                        "name": group_name
                    }
                }
        
        return named_groups
    
    def _calculate_multi_run_statistics(self, grouped_runs: Dict) -> Dict[str, Any]:
        """
        Calculate statistics across multiple runs in each group
        
        Args:
            grouped_runs: Runs grouped by configuration
            
        Returns:
            Dictionary with multi-run statistics
        """
        multi_run_stats = {}
        
        for group_name, group_data in grouped_runs.items():
            runs = group_data["runs"]
            
            # Collect data for each algorithm across runs
            algorithm_stats = {}
            
            for run in runs:
                aggregated_data = run.get("aggregated_data", {})
                
                for algo_name, algo_data in aggregated_data.items():
                    if algo_name not in algorithm_stats:
                        algorithm_stats[algo_name] = {
                            "avg_values": [],
                            "avg_times": [],
                            "win_rates": [],
                            "final_totals": [],
                            "execution_times": [],
                            "nodes_evaluated": [],
                            "configurations": []
                        }
                    
                    # Collect metrics
                    stats = algorithm_stats[algo_name]
                    stats["avg_values"].append(algo_data.get("avg_value", 0))
                    stats["avg_times"].append(algo_data.get("avg_time", 0))
                    stats["win_rates"].append(algo_data.get("win_rate", 0))
                    
                    # Collect raw final totals if available
                    final_totals = algo_data.get("final_totals", [])
                    if final_totals:
                        stats["final_totals"].extend(final_totals)
                    
                    # Collect execution times
                    exec_times = algo_data.get("execution_times", [])
                    if exec_times:
                        stats["execution_times"].extend(exec_times)
                    
                    # Record configuration
                    stats["configurations"].append({
                        "run": run["timestamp"],
                        "heuristic_stats": algo_data.get("by_heuristic", {})
                    })
            
            # Calculate statistics for each algorithm
            group_stats = {}
            for algo_name, stats_data in algorithm_stats.items():
                group_stats[algo_name] = self._calculate_algorithm_statistics(stats_data)
            
            multi_run_stats[group_name] = {
                "group_info": group_data["config_summary"],
                "run_count": len(runs),
                "algorithm_stats": group_stats
            }
        
        return multi_run_stats
    
    def _calculate_algorithm_statistics(self, stats_data: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for an algorithm across runs
        
        Args:
            stats_data: Collected data for an algorithm
            
        Returns:
            Dictionary with calculated statistics
        """
        # Helper function to safely calculate stats
        def safe_stats(values):
            if not values:
                return None
            values = np.array(values)
            return {
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "count": len(values)
            }
        
        # Calculate confidence interval
        def confidence_interval(values, confidence=0.95):
            if len(values) < 2:
                return None
            try:
                n = len(values)
                mean = np.mean(values)
                std_err = np.std(values) / np.sqrt(n)
                h = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)
                return [float(mean - h), float(mean + h)]
            except:
                return None
        
        # Calculate statistics for each metric
        stats_result = {}
        
        metrics = {
            "avg_value": stats_data.get("avg_values", []),
            "avg_time": stats_data.get("avg_times", []),
            "win_rate": stats_data.get("win_rates", []),
            "final_total": stats_data.get("final_totals", []),
            "execution_time": stats_data.get("execution_times", [])
        }
        
        for metric_name, values in metrics.items():
            if values:
                basic_stats = safe_stats(values)
                if basic_stats:
                    basic_stats["confidence_95"] = confidence_interval(values, 0.95)
                    stats_result[metric_name] = basic_stats
        
        # Additional calculated metrics
        if stats_data.get("avg_values") and stats_data.get("avg_times"):
            avg_values = np.array(stats_data["avg_values"])
            avg_times = np.array(stats_data["avg_times"])
            
            # Efficiency metric: value per second
            with np.errstate(divide='ignore', invalid='ignore'):
                efficiency = np.where(avg_times > 0, avg_values / avg_times, 0)
                stats_result["efficiency"] = safe_stats(efficiency[efficiency != 0])
        
        # Configuration diversity
        configs = stats_data.get("configurations", [])
        unique_runs = len(set(c["run"] for c in configs))
        stats_result["metadata"] = {
            "unique_runs": unique_runs,
            "total_configurations": len(configs),
            "data_points": {
                "avg_values": len(stats_data.get("avg_values", [])),
                "final_totals": len(stats_data.get("final_totals", []))
            }
        }
        
        return stats_result
    
    def generate_comparison_report(self, group1: str, group2: str) -> Dict[str, Any]:
        """
        Compare two groups of runs statistically
        
        Args:
            group1: First group name
            group2: Second group name
            
        Returns:
            Dictionary with comparison results
        """
        if group1 not in self.multi_run_stats or group2 not in self.multi_run_stats:
            return {"error": "One or both groups not found"}
        
        group1_stats = self.multi_run_stats[group1]
        group2_stats = self.multi_run_stats[group2]
        
        comparison = {
            "groups": [group1, group2],
            "timestamp": datetime.now().isoformat(),
            "comparisons": {}
        }
        
        # Compare common algorithms
        algo1_set = set(group1_stats["algorithm_stats"].keys())
        algo2_set = set(group2_stats["algorithm_stats"].keys())
        common_algorithms = algo1_set.intersection(algo2_set)
        
        for algo in common_algorithms:
            stats1 = group1_stats["algorithm_stats"][algo]
            stats2 = group2_stats["algorithm_stats"][algo]
            
            algo_comparison = {}
            
            # Compare each metric
            for metric in ["avg_value", "avg_time", "win_rate"]:
                if metric in stats1 and metric in stats2:
                    mean1 = stats1[metric]["mean"]
                    mean2 = stats2[metric]["mean"]
                    
                    # Calculate difference and percentage change
                    diff = mean2 - mean1
                    pct_change = (diff / abs(mean1)) * 100 if mean1 != 0 else float('inf')
                    
                    # Simple effect size (Cohen's d approximation)
                    if "std" in stats1[metric] and "std" in stats2[metric]:
                        pooled_std = np.sqrt(
                            (stats1[metric]["std"]**2 + stats2[metric]["std"]**2) / 2
                        )
                        if pooled_std > 0:
                            effect_size = diff / pooled_std
                        else:
                            effect_size = 0
                    else:
                        effect_size = None
                    
                    algo_comparison[metric] = {
                        "group1_mean": mean1,
                        "group2_mean": mean2,
                        "difference": diff,
                        "percent_change": pct_change,
                        "effect_size": effect_size,
                        "interpretation": self._interpret_effect(effect_size) if effect_size is not None else "N/A"
                    }
            
            comparison["comparisons"][algo] = algo_comparison
        
        return comparison
    
    def _interpret_effect(self, effect_size: float) -> str:
        """Interpret effect size magnitude"""
        if effect_size is None:
            return "No data"
        abs_effect = abs(effect_size)
        if abs_effect < 0.2:
            return "Negligible"
        elif abs_effect < 0.5:
            return "Small"
        elif abs_effect < 0.8:
            return "Medium"
        else:
            return "Large"
    
    def save_multi_run_analysis(self, output_dir: str = "multi_run_analysis") -> Dict[str, str]:
        """
        Save multi-run analysis results
        
        Args:
            output_dir: Directory to save analysis results
            
        Returns:
            Dictionary with paths to saved files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save multi-run statistics
        stats_file = output_path / f"multi_run_stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.multi_run_stats, f, indent=2, default=str)
        
        # Save group information
        groups_file = output_path / f"run_groups_{timestamp}.json"
        with open(groups_file, 'w') as f:
            json.dump({
                "aggregated_groups": self.aggregated_groups,
                "run_count": len(self.runs),
                "group_count": len(self.aggregated_groups)
            }, f, indent=2, default=str)
        
        # Generate summary report
        summary = self.generate_summary_report()
        summary_file = output_path / f"summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return {
            "stats": str(stats_file),
            "groups": str(groups_file),
            "summary": str(summary_file),
            "timestamp": timestamp
        }
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report"""
        if not self.multi_run_stats:
            return "No multi-run statistics available."
        
        report = []
        report.append("=" * 80)
        report.append("MULTI-RUN STATISTICAL ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total runs analyzed: {len(self.runs)}")
        report.append(f"Configuration groups: {len(self.multi_run_stats)}")
        report.append("")
        
        for group_name, group_stats in self.multi_run_stats.items():
            report.append(f"GROUP: {group_name}")
            report.append(f"  Runs in group: {group_stats['run_count']}")
            report.append(f"  Algorithms: {len(group_stats['algorithm_stats'])}")
            report.append("")
            
            # Summary for each algorithm
            for algo_name, algo_stats in group_stats["algorithm_stats"].items():
                report.append(f"  Algorithm: {algo_name}")
                
                if "avg_value" in algo_stats:
                    val = algo_stats["avg_value"]
                    ci = val.get("confidence_95", [0, 0])
                    report.append(f"    Average Value: {val['mean']:.2f} ± {val['std']:.2f}")
                    report.append(f"    95% CI: [{ci[0]:.2f}, {ci[1]:.2f}]")
                
                if "win_rate" in algo_stats:
                    wr = algo_stats["win_rate"]
                    report.append(f"    Win Rate: {wr['mean']:.1%} ± {wr['std']:.1%}")
                
                if "avg_time" in algo_stats:
                    time = algo_stats["avg_time"]
                    report.append(f"    Avg Time: {time['mean']:.4f}s ± {time['std']:.4f}s")
                
                report.append("")
        
        # Add comparison summary if we have multiple groups
        if len(self.multi_run_stats) >= 2:
            report.append("=" * 80)
            report.append("GROUP COMPARISONS")
            report.append("=" * 80)
            
            groups = list(self.multi_run_stats.keys())
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    comparison = self.generate_comparison_report(groups[i], groups[j])
                    
                    report.append(f"\nComparison: {groups[i]} vs {groups[j]}")
                    for algo, metrics in comparison.get("comparisons", {}).items():
                        report.append(f"  {algo}:")
                        for metric, data in metrics.items():
                            report.append(f"    {metric}: {data['difference']:+.3f} "
                                        f"({data['percent_change']:+.1f}%) "
                                        f"Effect: {data['interpretation']}")
        
        return "\n".join(report)


def analyze_multiple_runs(
    results_dir: str = "experiment_results/results",
    output_dir: str = "multi_run_analysis",
    pattern: str = "*"
) -> Dict[str, Any]:
    """
    Convenience function to analyze multiple runs
    
    Args:
        results_dir: Directory containing run directories
        output_dir: Directory to save analysis results
        pattern: Glob pattern for run directories
        
    Returns:
        Dictionary with analysis results
    """
    print("Starting multi-run analysis...")
    print(f"Results directory: {results_dir}")
    print(f"Pattern: {pattern}")
    
    aggregator = StatisticalAggregator(results_dir)
    
    print("Loading runs...")
    grouped_runs = aggregator.load_all_runs(pattern)
    
    print(f"Loaded {len(aggregator.runs)} runs")
    print(f"Grouped into {len(grouped_runs)} configuration groups")
    
    print("\nGenerating statistics...")
    saved_files = aggregator.save_multi_run_analysis(output_dir)
    
    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    for key, path in saved_files.items():
        if key != "timestamp":
            print(f"{key.capitalize()}: {path}")
    
    return {
        "aggregator": aggregator,
        "grouped_runs": grouped_runs,
        "multi_run_stats": aggregator.multi_run_stats,
        "saved_files": saved_files
    }


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze multiple experiment runs")
    parser.add_argument("--results-dir", default="experiment_results/results",
                       help="Directory containing experiment runs")
    parser.add_argument("--output-dir", default="multi_run_analysis",
                       help="Directory to save analysis results")
    parser.add_argument("--pattern", default="*",
                       help="Glob pattern for run directories")
    
    args = parser.parse_args()
    
    results = analyze_multiple_runs(
        results_dir=args.results_dir,
        output_dir=args.output_dir,
        pattern=args.pattern
    )
    
    # Print summary report
    print("\n" + results["aggregator"].generate_summary_report())