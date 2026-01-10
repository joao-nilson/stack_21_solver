#!/usr/bin/env python3
"""
Integrated Analysis - Combines all analysis tools with unified configuration
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config_manager import ConfigManager
from experiment_runner import ExperimentRunner


class IntegratedAnalysis:
    """Integrated analysis combining all tools with configuration"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.results = {}
    
    def run_comprehensive_analysis(self, preset_name: str = "comprehensive_benchmark"):
        """Run comprehensive analysis using configuration preset"""
        print("\n" + "="*80)
        print("INTEGRATED COMPREHENSIVE ANALYSIS")
        print("="*80)
        
        # Load configuration
        config = self.config_manager.load_preset(preset_name)
        
        # Run experiment
        runner = ExperimentRunner(config)
        results = runner.run_experiments()
        
        # Run additional analyses
        self.run_algorithm_comparison(results)
        self.run_heuristic_analysis(results)
        self.run_scalability_analysis(results)
        
        # Generate combined report
        self.generate_combined_report(results)
        
        self.results = results
        return results
    
    def run_algorithm_comparison(self, experiment_results):
        """Run algorithm comparison analysis"""
        print("\n" + "="*80)
        print("ALGORITHM COMPARISON ANALYSIS")
        print("="*80)
        
        # Group results by algorithm
        algo_results = {}
        for result in experiment_results:
            if "error" in result:
                continue
            algo = result["algorithm"]
            if algo not in algo_results:
                algo_results[algo] = []
            algo_results[algo].append(result)
        
        # Compare algorithms
        print("\nAlgorithm Performance:")
        print("-" * 80)
        print(f"{'Algorithm':<25} {'Avg Time':<12} {'Avg Value':<12} {'Wins':<8} {'Nodes/Sec':<12}")
        print("-" * 80)
        
        for algo, results_list in algo_results.items():
            avg_time = sum(r["execution_time"] for r in results_list) / len(results_list)
            avg_value = sum(r["value"] for r in results_list) / len(results_list)
            wins = sum(1 for r in results_list if r.get("is_21", False))
            avg_nodes = sum(r.get("statistics", {}).get("nodes_evaluated", 0) for r in results_list) / len(results_list)
            nodes_per_sec = avg_nodes / avg_time if avg_time > 0 else 0
            
            print(f"{algo:<25} {avg_time:<12.3f} {avg_value:<12.1f} {wins:<8} {nodes_per_sec:<12,.0f}")
    
    def run_heuristic_analysis(self, experiment_results):
        """Run heuristic analysis"""
        print("\n" + "="*80)
        print("HEURISTIC ANALYSIS")
        print("="*80)
        
        # Group results by heuristic
        heuristic_results = {}
        for result in experiment_results:
            if "error" in result:
                continue
            heuristic = result["heuristic"]
            if heuristic not in heuristic_results:
                heuristic_results[heuristic] = []
            heuristic_results[heuristic].append(result)
        
        print("\nHeuristic Performance:")
        print("-" * 80)
        print(f"{'Heuristic':<20} {'Avg Final':<12} {'Win Rate':<12} {'Bust Rate':<12} {'Avg Moves':<12}")
        print("-" * 80)
        
        for heuristic, results_list in heuristic_results.items():
            avg_final = sum(r.get("final_total", 0) for r in results_list) / len(results_list)
            wins = sum(1 for r in results_list if r.get("is_21", False))
            busts = sum(1 for r in results_list if r.get("is_bust", False))
            win_rate = wins / len(results_list) * 100
            bust_rate = busts / len(results_list) * 100
            avg_moves = sum(r.get("game_metrics", {}).get("moves_count", 0) for r in results_list) / len(results_list)
            
            print(f"{heuristic:<20} {avg_final:<12.1f} {win_rate:<12.1f}% {bust_rate:<12.1f}% {avg_moves:<12.1f}")
    
    def run_scalability_analysis(self, experiment_results):
        """Run scalability analysis with stack size"""
        print("\n" + "="*80)
        print("SCALABILITY ANALYSIS")
        print("="*80)
        
        # Group by stack length
        length_results = {}
        for result in experiment_results:
            if "error" in result:
                continue
            length = result.get("stack_length", 0)
            if length not in length_results:
                length_results[length] = []
            length_results[length].append(result)
        
        print("\nPerformance by Stack Length:")
        print("-" * 80)
        print(f"{'Length':<10} {'Avg Time':<12} {'Avg Nodes':<12} {'Time/Length':<12} {'Nodes/Length':<12}")
        print("-" * 80)
        
        for length, results_list in sorted(length_results.items()):
            avg_time = sum(r["execution_time"] for r in results_list) / len(results_list)
            avg_nodes = sum(r.get("statistics", {}).get("nodes_evaluated", 0) for r in results_list) / len(results_list)
            time_per_length = avg_time / length if length > 0 else 0
            nodes_per_length = avg_nodes / length if length > 0 else 0
            
            print(f"{length:<10} {avg_time:<12.3f} {avg_nodes:<12,.0f} {time_per_length:<12.3f} {nodes_per_length:<12,.0f}")
    
    def generate_combined_report(self, results):
        """Generate combined analysis report"""
        print("\n" + "="*80)
        print("COMBINED ANALYSIS REPORT")
        print("="*80)
        
        # Find best performing configurations
        successful_results = [r for r in results if "error" not in r]
        
        if not successful_results:
            print("No successful results to analyze")
            return
        
        # Best for reaching 21
        closest_results = sorted(
            successful_results,
            key=lambda x: abs(21 - x.get("final_total", 0))
        )[:5]
        
        print("\nBest configurations for reaching 21:")
        print("-" * 80)
        for result in closest_results:
            distance = abs(21 - result.get("final_total", 0))
            print(f"  Algorithm: {result['algorithm']}, "
                  f"Heuristic: {result['heuristic']}, "
                  f"Stack: {result['stack']}, "
                  f"Final: {result.get('final_total', 'N/A')} "
                  f"(Distance: {distance})")
        
        # Fastest executions
        fastest_results = sorted(
            successful_results,
            key=lambda x: x.get("execution_time", float('inf'))
        )[:5]
        
        print("\nFastest executions:")
        print("-" * 80)
        for result in fastest_results:
            print(f"  Algorithm: {result['algorithm']}, "
                  f"Heuristic: {result['heuristic']}, "
                  f"Stack: {result['stack']}, "
                  f"Time: {result.get('execution_time', 0):.3f}s")
        
        # Most efficient (nodes/time)
        efficient_results = sorted(
            successful_results,
            key=lambda x: x.get("statistics", {}).get("nodes_evaluated", 0) / 
                         max(x.get("execution_time", 0.001), 0.001),
            reverse=True
        )[:5]
        
        print("\nMost efficient (highest nodes/second):")
        print("-" * 80)
        for result in efficient_results:
            nodes = result.get("statistics", {}).get("nodes_evaluated", 0)
            time_taken = max(result.get("execution_time", 0.001), 0.001)
            efficiency = nodes / time_taken
            print(f"  Algorithm: {result['algorithm']}, "
                  f"Heuristic: {result['heuristic']}, "
                  f"Stack: {result['stack']}, "
                  f"Nodes/sec: {efficiency:,.0f}")


def main():
    """Main entry point for integrated analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrated analysis of Stack-based 21 algorithms")
    parser.add_argument("--preset", type=str, default="comprehensive_benchmark",
                       choices=["quick_test", "comprehensive_benchmark", 
                               "algorithm_comparison", "heuristic_analysis", 
                               "scalability_study"],
                       help="Configuration preset to use")
    
    args = parser.parse_args()
    
    try:
        analyzer = IntegratedAnalysis()
        results = analyzer.run_comprehensive_analysis(args.preset)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        
        # Generate output summary
        successful = len([r for r in results if "error" not in r])
        total = len(results)
        
        print(f"\nResults: {successful}/{total} successful ({successful/total*100:.1f}%)")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
