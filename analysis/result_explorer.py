"""
CLI Dashboard for interactive result exploration
"""
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .statistical_aggregator import StatisticalAggregator
from .comparative_visualizer import ComparativeVisualizer, visualize_run


class ResultExplorer:
    """
    CLI Dashboard for exploring experiment results
    """
    
    def __init__(self, results_base_dir: str = "experiment_results/results"):
        self.results_base_dir = Path(results_base_dir)
        self.aggregator = StatisticalAggregator(results_base_dir)
        self.current_runs = []
        self.current_group = None
        
    def discover_and_select_runs(self):
        """Discover runs and let user select which to analyze"""
        print("\n" + "="*80)
        print("DISCOVERING EXPERIMENT RUNS")
        print("="*80)
        
        run_dirs = self.aggregator.discover_runs()
        
        if not run_dirs:
            print("No experiment runs found!")
            return []
        
        print(f"\nFound {len(run_dirs)} experiment runs:")
        for i, run_dir in enumerate(run_dirs[:20]):  # Show first 20
            print(f"  {i+1:3}. {run_dir.name}")
        
        if len(run_dirs) > 20:
            print(f"  ... and {len(run_dirs) - 20} more")
        
        selection = input("\nSelect runs to analyze (comma-separated, 'all', or 'q' to quit): ").strip()
        
        if selection.lower() == 'q':
            return []
        elif selection.lower() == 'all':
            selected_dirs = run_dirs
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                selected_dirs = [run_dirs[i] for i in indices if 0 <= i < len(run_dirs)]
            except:
                print("Invalid selection!")
                return []
        
        return selected_dirs
    
    def load_selected_runs(self, run_dirs: List[Path]):
        """Load selected runs for analysis"""
        print(f"\nLoading {len(run_dirs)} runs...")
        
        self.current_runs = []
        for run_dir in run_dirs:
            run_data = self.aggregator.load_run(run_dir)
            if run_data:
                self.current_runs.append(run_data)
        
        # Group runs by configuration
        grouped_runs = self.aggregator._group_by_configuration(self.current_runs)
        
        print(f"\nLoaded {len(self.current_runs)} runs, grouped into {len(grouped_runs)} configuration groups")
        
        return grouped_runs
    
    def show_group_summary(self, grouped_runs: Dict):
        """Show summary of grouped runs"""
        print("\n" + "="*80)
        print("CONFIGURATION GROUPS")
        print("="*80)
        
        for group_name, group_data in grouped_runs.items():
            runs = group_data["runs"]
            config = group_data["config_summary"]
            
            print(f"\n{group_name}:")
            print(f"  Runs: {len(runs)}")
            print(f"  Algorithms: {config['algorithms']}")
            print(f"  Heuristics: {config['heuristics']}")
            print(f"  Stacks: {config['stacks']}")
            
            # Show timestamps
            timestamps = [run['timestamp'] for run in runs[:3]]
            if timestamps:
                print(f"  Recent runs: {', '.join(timestamps)}")
                if len(runs) > 3:
                    print(f"  ... and {len(runs) - 3} more")
    
    def analyze_single_run(self, run_dir: Path):
        """Analyze a single run interactively"""
        print(f"\nAnalyzing run: {run_dir.name}")
        
        # Load run data
        run_data = self.aggregator.load_run(run_dir)
        if not run_data:
            print("Failed to load run data!")
            return
        
        aggregated_data = run_data.get("aggregated_data", {})
        
        if not aggregated_data:
            print("No aggregated data found!")
            return
        
        print(f"\nAlgorithms in this run: {len(aggregated_data)}")
        
        while True:
            print("\n" + "-"*60)
            print("SINGLE RUN ANALYSIS MENU")
            print("-"*60)
            print("1. Show algorithm summary")
            print("2. Compare algorithms")
            print("3. Generate visualizations")
            print("4. Export analysis")
            print("5. Back to main menu")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                self._show_algorithm_summary(aggregated_data)
            elif choice == "2":
                self._compare_algorithms(aggregated_data)
            elif choice == "3":
                self._generate_run_visualizations(run_dir)
            elif choice == "4":
                self._export_run_analysis(run_dir, aggregated_data)
            elif choice == "5":
                break
            else:
                print("Invalid choice!")
    
    def analyze_multiple_runs(self, grouped_runs: Dict):
        """Analyze multiple runs statistically"""
        print("\n" + "="*80)
        print("MULTI-RUN STATISTICAL ANALYSIS")
        print("="*80)
        
        # Calculate statistics
        self.aggregator.runs = self.current_runs
        self.aggregator.aggregated_groups = grouped_runs
        multi_run_stats = self.aggregator._calculate_multi_run_statistics(grouped_runs)
        
        while True:
            print("\n" + "-"*60)
            print("MULTI-RUN ANALYSIS MENU")
            print("-"*60)
            print("1. Show group statistics")
            print("2. Compare groups")
            print("3. Generate statistical report")
            print("4. Generate comparison charts")
            print("5. Back to main menu")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                self._show_group_statistics(multi_run_stats)
            elif choice == "2":
                self._compare_groups_interactive(multi_run_stats)
            elif choice == "3":
                self._generate_statistical_report(multi_run_stats)
            elif choice == "4":
                self._generate_comparison_charts(multi_run_stats)
            elif choice == "5":
                break
            else:
                print("Invalid choice!")
    
    def _show_algorithm_summary(self, aggregated_data: Dict):
        """Show summary of algorithms in a run"""
        print("\n" + "-"*60)
        print("ALGORITHM SUMMARY")
        print("-"*60)
        
        for algo_name, algo_data in aggregated_data.items():
            print(f"\n{algo_name}:")
            print(f"  Count: {algo_data.get('count', 0)}")
            print(f"  Avg Value: {algo_data.get('avg_value', 0):.2f}")
            print(f"  Avg Time: {algo_data.get('avg_time', 0):.4f}s")
            print(f"  Win Rate: {algo_data.get('win_rate', 0):.1%}")
            print(f"  Final Total: {algo_data.get('avg_final_total', 0):.1f}")
            
            # Show heuristic breakdown if available
            by_heuristic = algo_data.get('by_heuristic', {})
            if by_heuristic:
                print(f"  By Heuristic:")
                for heuristic, stats in by_heuristic.items():
                    print(f"    {heuristic}: avg_value={stats.get('avg_value', 0):.2f}")
    
    def _compare_algorithms(self, aggregated_data: Dict):
        """Compare algorithms in a run"""
        print("\n" + "-"*60)
        print("ALGORITHM COMPARISON")
        print("-"*60)
        
        # Sort by average value
        sorted_algorithms = sorted(
            aggregated_data.items(),
            key=lambda x: x[1].get('avg_value', 0),
            reverse=True
        )
        
        print(f"\n{'Algorithm':<25} {'Avg Value':<12} {'Avg Time':<12} {'Win Rate':<12}")
        print("-" * 65)
        
        for algo_name, algo_data in sorted_algorithms:
            print(f"{algo_name:<25} "
                  f"{algo_data.get('avg_value', 0):<12.2f} "
                  f"{algo_data.get('avg_time', 0):<12.4f} "
                  f"{algo_data.get('win_rate', 0):<12.1%}")
        
        # Find best algorithm
        if sorted_algorithms:
            best_algo, best_data = sorted_algorithms[0]
            print(f"\nBest algorithm: {best_algo} with avg_value={best_data.get('avg_value', 0):.2f}")
    
    def _generate_run_visualizations(self, run_dir: Path):
        """Generate visualizations for a run"""
        print(f"\nGenerating visualizations for {run_dir.name}...")
        
        try:
            charts = visualize_run(str(run_dir))
            print(f"\nGenerated {len(charts) - 1} charts:")
            for name, path in charts.items():
                if name != "index":
                    print(f"  ✓ {name}: {path.name}")
        except Exception as e:
            print(f"Error generating visualizations: {e}")
    
    def _export_run_analysis(self, run_dir: Path, aggregated_data: Dict):
        """Export analysis for a run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = run_dir / f"analysis_summary_{timestamp}.txt"
        
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"ANALYSIS SUMMARY: {run_dir.name}\n")
            f.write("="*80 + "\n\n")
            
            f.write("ALGORITHM PERFORMANCE:\n")
            f.write("-"*40 + "\n")
            
            for algo_name, algo_data in aggregated_data.items():
                f.write(f"\n{algo_name}:\n")
                f.write(f"  Count: {algo_data.get('count', 0)}\n")
                f.write(f"  Avg Value: {algo_data.get('avg_value', 0):.2f}\n")
                f.write(f"  Avg Time: {algo_data.get('avg_time', 0):.4f}s\n")
                f.write(f"  Win Rate: {algo_data.get('win_rate', 0):.1%}\n")
        
        print(f"Analysis exported to: {output_file}")
    
    def _show_group_statistics(self, multi_run_stats: Dict):
        """Show statistics for groups"""
        print("\n" + "-"*60)
        print("GROUP STATISTICS")
        print("-"*60)
        
        for group_name, group_data in multi_run_stats.items():
            print(f"\n{group_name}:")
            print(f"  Runs: {group_data.get('run_count', 0)}")
            
            algo_stats = group_data.get('algorithm_stats', {})
            print(f"  Algorithms: {len(algo_stats)}")
            
            # Show top algorithm by avg_value
            if algo_stats:
                best_algo = max(algo_stats.items(), 
                              key=lambda x: x[1].get('avg_value', {}).get('mean', 0))
                algo_name, stats = best_algo
                avg_value = stats.get('avg_value', {}).get('mean', 0)
                print(f"  Best Algorithm: {algo_name} (avg_value={avg_value:.2f})")
    
    def _compare_groups_interactive(self, multi_run_stats: Dict):
        """Interactively compare groups"""
        groups = list(multi_run_stats.keys())
        
        if len(groups) < 2:
            print("Need at least 2 groups for comparison!")
            return
        
        print("\nAvailable groups:")
        for i, group in enumerate(groups):
            print(f"  {i+1}. {group}")
        
        try:
            choice1 = int(input("\nSelect first group (number): ")) - 1
            choice2 = int(input("Select second group (number): ")) - 1
            
            if 0 <= choice1 < len(groups) and 0 <= choice2 < len(groups):
                group1 = groups[choice1]
                group2 = groups[choice2]
                
                comparison = self.aggregator.generate_comparison_report(group1, group2)
                
                print(f"\nComparison: {group1} vs {group2}")
                print("-"*60)
                
                for algo, metrics in comparison.get('comparisons', {}).items():
                    print(f"\n{algo}:")
                    for metric, data in metrics.items():
                        diff = data.get('difference', 0)
                        pct = data.get('percent_change', 0)
                        print(f"  {metric}: {diff:+.3f} ({pct:+.1f}%)")
                
            else:
                print("Invalid group selection!")
        except ValueError:
            print("Invalid input!")
    
    def _generate_statistical_report(self, multi_run_stats: Dict):
        """Generate statistical report"""
        report = self.aggregator.generate_summary_report()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path("multi_run_analysis") / f"statistical_report_{timestamp}.txt"
        output_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"\nStatistical report saved to: {output_file}")
        
        # Print a preview
        print("\nReport preview (first 20 lines):")
        print("-"*60)
        for line in report.split('\n')[:20]:
            print(line)
    
    def _generate_comparison_charts(self, multi_run_stats: Dict):
        """Generate comparison charts for multi-run analysis"""
        print("\nGenerating comparison charts...")
        
        visualizer = ComparativeVisualizer("multi_run_analysis/charts")
        
        try:
            # Generate multi-run comparison chart
            chart_path = visualizer.generate_multi_run_comparison_chart(
                multi_run_stats,
                metric="avg_value",
                output_filename="multi_run_comparison"
            )
            print(f"✓ Generated: {chart_path}")
            
            # Generate additional charts for different metrics
            for metric in ["win_rate", "avg_time"]:
                try:
                    chart_path = visualizer.generate_multi_run_comparison_chart(
                        multi_run_stats,
                        metric=metric,
                        output_filename=f"multi_run_comparison_{metric}"
                    )
                    print(f"✓ Generated: {chart_path}")
                except Exception as e:
                    print(f"✗ Failed to generate {metric} chart: {e}")
                    
        except Exception as e:
            print(f"Error generating charts: {e}")
    
    def interactive_menu(self):
        """Main interactive menu"""
        while True:
            print("\n" + "="*80)
            print("EXPERIMENT RESULT EXPLORER")
            print("="*80)
            print("1. Discover and analyze runs")
            print("2. Analyze specific run directory")
            print("3. Load previously analyzed runs")
            print("4. Generate comprehensive report")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                self._menu_discover_and_analyze()
            elif choice == "2":
                self._menu_analyze_specific()
            elif choice == "3":
                if self.current_runs:
                    self._menu_analyze_current()
                else:
                    print("No runs loaded! Use option 1 first.")
            elif choice == "4":
                self._menu_generate_report()
            elif choice == "5":
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice!")
    
    def _menu_discover_and_analyze(self):
        """Menu for discovering and analyzing runs"""
        run_dirs = self.discover_and_select_runs()
        if not run_dirs:
            return
        
        grouped_runs = self.load_selected_runs(run_dirs)
        
        while True:
            print("\n" + "-"*60)
            print("ANALYSIS OPTIONS")
            print("-"*60)
            print("1. Show group summary")
            print("2. Analyze single run")
            print("3. Analyze multiple runs statistically")
            print("4. Back to main menu")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                self.show_group_summary(grouped_runs)
            elif choice == "2":
                # Let user select which run to analyze
                print("\nAvailable runs:")
                for i, run in enumerate(self.current_runs):
                    print(f"  {i+1}. {run['timestamp']}")
                
                try:
                    run_idx = int(input("\nSelect run to analyze (number): ")) - 1
                    if 0 <= run_idx < len(self.current_runs):
                        run_dir = Path(self.current_runs[run_idx]['run_dir'])
                        self.analyze_single_run(run_dir)
                    else:
                        print("Invalid selection!")
                except ValueError:
                    print("Invalid input!")
            elif choice == "3":
                self.analyze_multiple_runs(grouped_runs)
            elif choice == "4":
                break
            else:
                print("Invalid choice!")
    
    def _menu_analyze_specific(self):
        """Menu for analyzing a specific run directory"""
        run_path = input("\nEnter path to run directory: ").strip()
        
        if not run_path:
            print("No path provided!")
            return
        
        run_dir = Path(run_path)
        if not run_dir.exists():
            print(f"Directory not found: {run_dir}")
            return
        
        self.analyze_single_run(run_dir)
    
    def _menu_analyze_current(self):
        """Menu for analyzing currently loaded runs"""
        if not self.current_runs:
            print("No runs currently loaded!")
            return
        
        grouped_runs = self.aggregator._group_by_configuration(self.current_runs)
        self.analyze_multiple_runs(grouped_runs)
    
    def _menu_generate_report(self):
        """Menu for generating comprehensive report"""
        print("\n" + "-"*60)
        print("GENERATE COMPREHENSIVE REPORT")
        print("-"*60)
        print("1. Generate report for specific run")
        print("2. Generate multi-run statistical report")
        print("3. Back to main menu")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            run_path = input("\nEnter path to run directory: ").strip()
            if run_path:
                run_dir = Path(run_path)
                if run_dir.exists():
                    self._generate_run_visualizations(run_dir)
                else:
                    print(f"Directory not found: {run_dir}")
        elif choice == "2":
            if self.current_runs:
                grouped_runs = self.aggregator._group_by_configuration(self.current_runs)
                multi_run_stats = self.aggregator._calculate_multi_run_statistics(grouped_runs)
                self._generate_statistical_report(multi_run_stats)
            else:
                print("No runs loaded! Use option 1 from main menu first.")
        elif choice == "3":
            return
        else:
            print("Invalid choice!")


def main():
    """Main entry point for CLI dashboard"""
    print("\n" + "="*80)
    print("STACK-BASED 21 SOLVER - RESULT EXPLORER")
    print("="*80)
    
    explorer = ResultExplorer()
    
    try:
        explorer.interactive_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()