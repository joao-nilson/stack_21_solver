"""
Comparative Visualization Generator using matplotlib and seaborn
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import matplotlib

# Configure matplotlib for better visuals
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ComparativeVisualizer:
    """
    Generates comparative visualizations for algorithm performance
    """
    
    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Set up color schemes
        self.colors = sns.color_palette("husl", 8)
        self.marker_styles = ['o', 's', '^', 'D', 'v', '<', '>', 'p']
        
        print(f"Visualizations will be saved to: {self.output_dir}")
    
    def load_aggregated_data(self, aggregated_file: Path) -> Dict[str, Any]:
        """
        Load aggregated results data
        
        Args:
            aggregated_file: Path to aggregated_results.json
            
        Returns:
            Dictionary with aggregated data
        """
        with open(aggregated_file, 'r') as f:
            return json.load(f)
    
    def load_multi_run_stats(self, stats_file: Path) -> Dict[str, Any]:
        """
        Load multi-run statistics data
        
        Args:
            stats_file: Path to multi_run_stats.json
            
        Returns:
            Dictionary with multi-run statistics
        """
        with open(stats_file, 'r') as f:
            return json.load(f)
    
    def generate_algorithm_comparison_chart(
        self,
        aggregated_data: Dict[str, Any],
        output_filename: Optional[str] = None,
        metrics: List[str] = ["avg_value", "avg_time", "win_rate"]
    ) -> Path:
        """
        Generate bar charts comparing algorithms
        
        Args:
            aggregated_data: Data from aggregated_results.json
            output_filename: Output filename (without extension)
            metrics: List of metrics to plot
            
        Returns:
            Path to saved chart
        """
        if not aggregated_data:
            raise ValueError("No aggregated data provided")
        
        # Prepare data for plotting
        algorithms = list(aggregated_data.keys())
        
        # Create subplots for each metric
        fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 4 * len(metrics)))
        if len(metrics) == 1:
            axes = [axes]
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            
            # Extract metric values for each algorithm
            values = []
            errors = []
            algo_names = []
            
            for algo in algorithms:
                algo_data = aggregated_data[algo]
                
                if metric == "avg_value":
                    value = algo_data.get("avg_value", 0)
                    # Use std of final_totals if available
                    if "final_totals" in algo_data and algo_data["final_totals"]:
                        error = np.std(algo_data["final_totals"])
                    else:
                        error = 0
                elif metric == "avg_time":
                    value = algo_data.get("avg_time", 0)
                    # Use std of execution_times if available
                    if "execution_times" in algo_data and algo_data["execution_times"]:
                        error = np.std(algo_data["execution_times"])
                    else:
                        error = 0
                elif metric == "win_rate":
                    value = algo_data.get("win_rate", 0) * 100  # Convert to percentage
                    error = 0  # No error bars for win rate
                else:
                    value = algo_data.get(metric, 0)
                    error = 0
                
                values.append(value)
                errors.append(error)
                algo_names.append(algo)
            
            # Create bar chart with error bars
            x_pos = np.arange(len(algorithms))
            bars = ax.bar(x_pos, values, yerr=errors, capsize=5, 
                         color=self.colors[:len(algorithms)],
                         edgecolor='black', linewidth=1.2)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(errors)*0.1,
                       f'{height:.2f}', ha='center', va='bottom', fontsize=9)
            
            # Customize axes
            ax.set_xticks(x_pos)
            ax.set_xticklabels(algo_names, rotation=45, ha='right')
            ax.set_ylabel(self._get_metric_label(metric))
            ax.set_title(f'Algorithm Comparison - {self._get_metric_label(metric)}')
            
            # Add grid
            ax.grid(True, alpha=0.3, linestyle='--')
        
        # Adjust layout and save
        plt.tight_layout()
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"algorithm_comparison_{timestamp}"
        
        output_path = self.output_dir / f"{output_filename}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved algorithm comparison chart to: {output_path}")
        return output_path
    
    def generate_multi_run_comparison_chart(
        self,
        multi_run_stats: Dict[str, Any],
        metric: str = "avg_value",
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate comparison chart with confidence intervals across multiple runs
        
        Args:
            multi_run_stats: Multi-run statistics data
            metric: Metric to compare (avg_value, win_rate, avg_time)
            output_filename: Output filename
            
        Returns:
            Path to saved chart
        """
        if not multi_run_stats:
            raise ValueError("No multi-run statistics provided")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Prepare data
        all_algorithms = set()
        group_data = {}
        
        for group_name, group_stats in multi_run_stats.items():
            algo_stats = group_stats.get("algorithm_stats", {})
            group_data[group_name] = {}
            
            for algo_name, stats in algo_stats.items():
                all_algorithms.add(algo_name)
                if metric in stats:
                    group_data[group_name][algo_name] = stats[metric]
        
        # Create grouped bar chart with error bars
        algorithms = sorted(list(all_algorithms))
        groups = list(group_data.keys())
        
        x = np.arange(len(algorithms))
        width = 0.8 / len(groups)
        
        for i, group in enumerate(groups):
            means = []
            errors = []
            cis = []
            
            for algo in algorithms:
                if algo in group_data[group]:
                    data = group_data[group][algo]
                    means.append(data["mean"])
                    errors.append(data["std"])
                    if "confidence_95" in data:
                        ci = data["confidence_95"]
                        ci_width = (ci[1] - ci[0]) / 2 if ci else data["std"]
                        cis.append(ci_width)
                    else:
                        cis.append(data["std"])
                else:
                    means.append(0)
                    errors.append(0)
                    cis.append(0)
            
            # Use confidence intervals for error bars if available
            error_bars = cis if any(cis) else errors
            
            bars = ax.bar(x + i * width - (len(groups) - 1) * width / 2, 
                         means, width, label=group,
                         yerr=error_bars, capsize=4,
                         color=self.colors[i % len(self.colors)],
                         edgecolor='black', linewidth=1)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}', ha='center', va='bottom',
                           fontsize=8, fontweight='bold')
        
        # Customize chart
        ax.set_xlabel('Algorithm')
        ax.set_ylabel(self._get_metric_label(metric))
        ax.set_title(f'Multi-Run Comparison: {self._get_metric_label(metric)} '
                    f'with 95% Confidence Intervals')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        ax.legend(title='Configuration Group')
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Add overall stats annotation
        total_runs = sum(group_stats.get("run_count", 0) 
                        for group_stats in multi_run_stats.values())
        ax.text(0.02, 0.98, f'Total Runs Analyzed: {total_runs}',
                transform=ax.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"multi_run_comparison_{metric}_{timestamp}"
        
        output_path = self.output_dir / f"{output_filename}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved multi-run comparison chart to: {output_path}")
        return output_path
    
    def generate_heatmap(
        self,
        aggregated_data: Dict[str, Any],
        metric: str = "avg_value",
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate heatmap of algorithm performance
        
        Args:
            aggregated_data: Aggregated results data
            metric: Metric to visualize
            output_filename: Output filename
            
        Returns:
            Path to saved heatmap
        """
        # Extract algorithm and heuristic data
        heatmap_data = {}
        
        for algo_name, algo_data in aggregated_data.items():
            by_heuristic = algo_data.get("by_heuristic", {})
            
            for heuristic_name, heuristic_data in by_heuristic.items():
                if metric == "avg_value":
                    value = heuristic_data.get("avg_value", 0)
                elif metric == "win_rate":
                    value = heuristic_data.get("win_rate", 0)
                else:
                    value = 0
                
                if algo_name not in heatmap_data:
                    heatmap_data[algo_name] = {}
                heatmap_data[algo_name][heuristic_name] = value
        
        if not heatmap_data:
            raise ValueError("No heuristic data available for heatmap")
        
        # Convert to matrix
        algorithms = sorted(list(heatmap_data.keys()))
        heuristics = set()
        for algo_data in heatmap_data.values():
            heuristics.update(algo_data.keys())
        heuristics = sorted(list(heuristics))
        
        matrix = np.zeros((len(algorithms), len(heuristics)))
        
        for i, algo in enumerate(algorithms):
            for j, heuristic in enumerate(heuristics):
                matrix[i, j] = heatmap_data[algo].get(heuristic, 0)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(max(8, len(heuristics) * 1.5), 
                                       max(6, len(algorithms) * 0.8)))
        
        # Use diverging colormap for better contrast
        cmap = sns.diverging_palette(220, 20, as_cmap=True)
        
        sns.heatmap(matrix, annot=True, fmt=".2f", cmap=cmap,
                   xticklabels=heuristics, yticklabels=algorithms,
                   ax=ax, cbar_kws={'label': self._get_metric_label(metric)},
                   linewidths=1, linecolor='white')
        
        ax.set_title(f'Algorithm × Heuristic Performance: {self._get_metric_label(metric)}')
        ax.set_xlabel('Heuristic')
        ax.set_ylabel('Algorithm')
        
        plt.tight_layout()
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"heatmap_{metric}_{timestamp}"
        
        output_path = self.output_dir / f"{output_filename}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved heatmap to: {output_path}")
        return output_path
    
    def generate_scalability_chart(
        self,
        raw_results: List[Dict[str, Any]],
        metric: str = "execution_time",
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate scalability chart (performance vs stack size)
        
        Args:
            raw_results: List of individual experiment results
            metric: Metric to plot against stack size
            output_filename: Output filename
            
        Returns:
            Path to saved chart
        """
        if not raw_results:
            raise ValueError("No raw results provided")
        
        # Group data by algorithm and stack length
        scalability_data = {}
        
        for result in raw_results:
            if "error" in result:
                continue
            
            algo = result.get("algorithm", "Unknown")
            stack_length = result.get("stack_length", 0)
            heuristic = result.get("heuristic", "Unknown")
            
            key = f"{algo} ({heuristic})"
            
            if key not in scalability_data:
                scalability_data[key] = {}
            
            if stack_length not in scalability_data[key]:
                scalability_data[key][stack_length] = []
            
            if metric == "execution_time":
                value = result.get("execution_time", 0)
            elif metric == "value":
                value = result.get("value", 0)
            elif metric == "final_total":
                value = result.get("final_total", 0)
            else:
                value = result.get(metric, 0)
            
            scalability_data[key][stack_length].append(value)
        
        # Create line chart
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for i, (algo_heuristic, length_data) in enumerate(scalability_data.items()):
            lengths = sorted(length_data.keys())
            means = []
            stds = []
            
            for length in lengths:
                values = length_data[length]
                means.append(np.mean(values))
                stds.append(np.std(values))
            
            # Plot line with error bars
            ax.errorbar(lengths, means, yerr=stds,
                       label=algo_heuristic,
                       marker=self.marker_styles[i % len(self.marker_styles)],
                       markersize=8, linewidth=2, capsize=5,
                       color=self.colors[i % len(self.colors)])
        
        # Customize chart
        ax.set_xlabel('Stack Length')
        ax.set_ylabel(self._get_metric_label(metric))
        ax.set_title(f'Scalability Analysis: {self._get_metric_label(metric)} vs Stack Length')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add trend line for overall pattern
        if len(scalability_data) > 0:
            # Get all data points
            all_lengths = []
            all_values = []
            
            for length_data in scalability_data.values():
                for length, values in length_data.items():
                    all_lengths.extend([length] * len(values))
                    all_values.extend(values)
            
            if len(all_lengths) > 1:
                # Fit polynomial trend
                z = np.polyfit(all_lengths, all_values, 2)
                p = np.poly1d(z)
                
                # Plot trend line
                x_trend = np.linspace(min(all_lengths), max(all_lengths), 100)
                ax.plot(x_trend, p(x_trend), 'k--', alpha=0.5, 
                       label='Overall Trend', linewidth=2)
        
        plt.tight_layout()
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"scalability_{metric}_{timestamp}"
        
        output_path = self.output_dir / f"{output_filename}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved scalability chart to: {output_path}")
        return output_path
    
    def generate_distribution_charts(
        self,
        aggregated_data: Dict[str, Any],
        metric: str = "final_totals",
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate distribution charts (histograms, box plots)
        
        Args:
            aggregated_data: Aggregated results data
            metric: Metric to visualize distribution of
            output_filename: Output filename
            
        Returns:
            Path to saved chart
        """
        # Extract distribution data
        distribution_data = []
        labels = []
        
        for algo_name, algo_data in aggregated_data.items():
            if metric in algo_data and algo_data[metric]:
                distribution_data.append(algo_data[metric])
                labels.append(algo_name)
        
        if not distribution_data:
            raise ValueError(f"No {metric} data available")
        
        # Create subplots
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Box plot
        bp = axes[0].boxplot(distribution_data, labels=labels, patch_artist=True)
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], self.colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        axes[0].set_title(f'Distribution of {self._get_metric_label(metric)} - Box Plot')
        axes[0].set_ylabel(self._get_metric_label(metric))
        axes[0].grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Histogram
        for i, (data, label) in enumerate(zip(distribution_data, labels)):
            axes[1].hist(data, bins=20, alpha=0.5, label=label,
                        color=self.colors[i % len(self.colors)])
        
        axes[1].set_title(f'Distribution of {self._get_metric_label(metric)} - Histogram')
        axes[1].set_xlabel(self._get_metric_label(metric))
        axes[1].set_ylabel('Frequency')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, linestyle='--')
        
        # Add statistics annotation
        stats_text = []
        for i, (data, label) in enumerate(zip(distribution_data, labels)):
            if len(data) > 0:
                stats_text.append(
                    f"{label}: μ={np.mean(data):.2f}, σ={np.std(data):.2f}, "
                    f"min={np.min(data):.2f}, max={np.max(data):.2f}"
                )
        
        fig.text(0.02, 0.02, '\n'.join(stats_text), fontsize=9,
                verticalalignment='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout(rect=[0, 0.1, 1, 0.95])
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"distribution_{metric}_{timestamp}"
        
        output_path = self.output_dir / f"{output_filename}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved distribution charts to: {output_path}")
        return output_path
    
    def generate_comprehensive_report(
        self,
        run_dir: Path,
        output_filename: Optional[str] = None
    ) -> Dict[str, Path]:
        """
        Generate a comprehensive visualization report for a run
        
        Args:
            run_dir: Path to run directory
            output_filename: Base output filename
            
        Returns:
            Dictionary mapping chart names to file paths
        """
        # Load data
        aggregated_file = run_dir / "aggregated_results.json"
        results_file = run_dir / "experiment_results.json"
        
        if not aggregated_file.exists():
            raise FileNotFoundError(f"No aggregated results found in {run_dir}")
        
        aggregated_data = self.load_aggregated_data(aggregated_file)
        
        raw_results = []
        if results_file.exists():
            with open(results_file, 'r') as f:
                raw_results = json.load(f)
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"comprehensive_report_{timestamp}"
        
        # Generate all charts
        charts = {}
        
        try:
            # 1. Algorithm comparison
            charts["algorithm_comparison"] = self.generate_algorithm_comparison_chart(
                aggregated_data,
                output_filename=f"{output_filename}_algorithm_comparison"
            )
            
            # 2. Heatmap (if heuristic data available)
            try:
                charts["heatmap"] = self.generate_heatmap(
                    aggregated_data,
                    metric="avg_value",
                    output_filename=f"{output_filename}_heatmap"
                )
            except ValueError:
                print("Skipping heatmap (no heuristic data)")
            
            # 3. Scalability chart (if raw results available)
            if raw_results and len(raw_results) > 10:
                try:
                    charts["scalability"] = self.generate_scalability_chart(
                        raw_results,
                        metric="execution_time",
                        output_filename=f"{output_filename}_scalability"
                    )
                except Exception as e:
                    print(f"Skipping scalability chart: {e}")
            
            # 4. Distribution charts
            try:
                charts["distribution"] = self.generate_distribution_charts(
                    aggregated_data,
                    metric="final_totals",
                    output_filename=f"{output_filename}_distribution"
                )
            except ValueError:
                print("Skipping distribution charts")
            
            # 5. Win rate comparison
            try:
                charts["win_rate"] = self.generate_algorithm_comparison_chart(
                    aggregated_data,
                    output_filename=f"{output_filename}_win_rate",
                    metrics=["win_rate"]
                )
            except Exception as e:
                print(f"Skipping win rate chart: {e}")
            
        except Exception as e:
            print(f"Error generating comprehensive report: {e}")
        
        # Save chart list
        charts_file = self.output_dir / f"{output_filename}_charts.json"
        with open(charts_file, 'w') as f:
            json.dump({
                "run_dir": str(run_dir),
                "charts": {k: str(v) for k, v in charts.items()},
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        
        charts["index"] = charts_file
        
        return charts
    
    def _get_metric_label(self, metric: str) -> str:
        """Get human-readable label for a metric"""
        labels = {
            "avg_value": "Average Value",
            "avg_time": "Average Time (seconds)",
            "win_rate": "Win Rate (%)",
            "final_totals": "Final Total",
            "execution_time": "Execution Time (seconds)",
            "value": "Value",
            "final_total": "Final Total",
            "nodes_evaluated": "Nodes Evaluated"
        }
        return labels.get(metric, metric.replace("_", " ").title())


def visualize_run(
    run_dir: str,
    output_dir: Optional[str] = None
) -> Dict[str, Path]:
    """
    Convenience function to visualize a single run
    
    Args:
        run_dir: Path to run directory
        output_dir: Directory to save visualizations
        
    Returns:
        Dictionary of generated chart paths
    """
    run_path = Path(run_dir)
    
    if output_dir is None:
        output_dir = run_path / "visualizations"
    
    visualizer = ComparativeVisualizer(output_dir)
    
    print(f"Generating visualizations for: {run_path}")
    print(f"Output directory: {output_dir}")
    
    charts = visualizer.generate_comprehensive_report(run_path)
    
    print("\nGenerated charts:")
    for name, path in charts.items():
        if name != "index":
            print(f"  • {name}: {path}")
    
    return charts


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate comparative visualizations")
    parser.add_argument("--run-dir", required=True,
                       help="Path to experiment run directory")
    parser.add_argument("--output-dir",
                       help="Directory to save visualizations")
    
    args = parser.parse_args()
    
    try:
        charts = visualize_run(args.run_dir, args.output_dir)
        print(f"\nVisualization complete! See index: {charts.get('index')}")
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()