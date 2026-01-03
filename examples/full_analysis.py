"""
Full Analysis: Comprehensive analysis of Stack-based 21 solver.
FIXED VERSION - avoids circular references and fixes evaluation.
"""

import sys
import os
import json
import time
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.stack_manager import StackManager
from src.game.game_state import GameState
from src.algorithms.minimax import MinimaxSolver
from src.algorithms.alphabeta import alphabeta_with_tracking, AlphaBetaSolver
from src.algorithms.solution_tracker import SolutionTracker
from src.utils.logger import GameLogger


class FixedGameAnalyzer:
    """Comprehensive analyzer for Stack-based 21 games (FIXED)."""
    
    def __init__(self, log_level="INFO"):
        """Initialize analyzer with logging."""
        self.logger = GameLogger(name="FixedAnalyzer", log_level=log_level)
        self.results = {}
        
    def analyze_game(self, stack, algorithm="both", depth_limit=None):
        """
        Run full analysis on a game with given stack.
        
        Args:
            stack: Game stack
            algorithm: "minimax", "alphabeta", or "both"
            depth_limit: Maximum search depth
        """
        self.logger.log_game_start(stack, algorithm, depth_limit)
        
        # Store stack info
        stack_info = StackManager.analyze_stack(stack)
        self.results["stack_info"] = stack_info
        
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        # Run algorithms
        if algorithm in ["minimax", "both"]:
            self._run_minimax_analysis(initial_state, depth_limit)
        
        if algorithm in ["alphabeta", "both"]:
            self._run_alphabeta_analysis(initial_state, depth_limit)
        
        # Compare algorithms if both were run
        if algorithm == "both":
            self._compare_algorithms()
        
        return self.results
    
    def _run_minimax_analysis(self, initial_state, depth_limit):
        """Run and analyze minimax algorithm."""
        self.logger.logger.info("Running Minimax analysis...")
        
        solver = MinimaxSolver(depth_limit=depth_limit)
        
        start_time = time.time()
        value, best_child = solver.solve(initial_state)
        execution_time = time.time() - start_time
        
        stats = solver.get_statistics()
        stats["execution_time"] = execution_time
        
        # Find optimal path
        path = solver.find_optimal_path(initial_state)
        
        # Store results (without circular references)
        self.results["minimax"] = {
            "value": value,
            "best_first_move": best_child.move_from_parent if best_child else None,
            "statistics": stats,
            "path_length": len(path) if path else 0,
            "terminal_total": path[-1].total if path else None,
            "move_sequence": self._extract_move_sequence(path)
        }
        
        # Log summary
        if path:
            self.logger.logger.info(f"Minimax solution: {len(path)-1} moves, final total: {path[-1].total}")
        
        return stats, path
    
    def _run_alphabeta_analysis(self, initial_state, depth_limit):
        """Run and analyze alpha-beta pruning algorithm."""
        self.logger.logger.info("Running Alpha-Beta analysis...")
        
        tracker = SolutionTracker()
        
        start_time = time.time()
        value, terminal_state = alphabeta_with_tracking(
            initial_state,
            depth=0,
            alpha=float('-inf'),
            beta=float('inf'),
            is_maximizing=True,
            tracker=tracker,
            depth_limit=depth_limit
        )
        execution_time = time.time() - start_time
        
        # Reconstruct path
        path = tracker.reconstruct_solution_path(initial_state, terminal_state)
        
        # Get summary
        summary = tracker.get_solution_summary()
        summary["execution_time"] = execution_time
        
        # Store results
        self.results["alphabeta"] = {
            "value": value,
            "summary": summary,
            "move_sequence": self._extract_move_sequence(path)
        }
        
        # Log summary
        if path:
            self.logger.logger.info(f"Alpha-beta solution: {len(path)-1} moves, final total: {path[-1].total}")
        
        return summary, path
    
    def _extract_move_sequence(self, path):
        """Extract move sequence from path without GameState objects."""
        if not path:
            return []
        
        sequence = []
        for i in range(1, len(path)):
            state = path[i]
            if state.move_from_parent:
                sequence.append({
                    'turn': i,
                    'value_taken': state.move_from_parent[0],
                    'value_discarded': state.move_from_parent[1],
                    'new_total': state.total,
                    'player': 'MAX' if not state.is_maximizing else 'MIN'
                })
        
        return sequence
    
    def _compare_algorithms(self):
        """Compare minimax and alpha-beta results."""
        if "minimax" not in self.results or "alphabeta" not in self.results:
            return
        
        minimax_stats = self.results["minimax"]["statistics"]
        alphabeta_stats = self.results["alphabeta"]["summary"]
        
        # Check if values match (within tolerance)
        value_diff = abs(self.results["minimax"]["value"] - self.results["alphabeta"]["value"])
        values_match = value_diff < 0.001
        
        comparison = {
            "value_difference": value_diff,
            "values_match": values_match,
            "minimax_nodes": minimax_stats.get("nodes_evaluated", 0),
            "alphabeta_nodes": alphabeta_stats.get("nodes_evaluated", 0),
            "minimax_time": minimax_stats.get("execution_time", 0),
            "alphabeta_time": alphabeta_stats.get("execution_time", 0),
            "pruning_efficiency": alphabeta_stats.get("pruning_efficiency", 0)
        }
        
        if alphabeta_stats.get("nodes_evaluated", 0) > 0:
            comparison["speedup_factor"] = minimax_stats.get("nodes_evaluated", 0) / alphabeta_stats.get("nodes_evaluated", 0)
            comparison["nodes_saved"] = minimax_stats.get("nodes_evaluated", 0) - alphabeta_stats.get("nodes_evaluated", 0)
        
        self.results["comparison"] = comparison
        
        self.logger.logger.info(f"Algorithm comparison: {comparison}")
    
    def export_results(self, filename="fixed_analysis_results.json"):
        """Export all analysis results to JSON file."""
        output_dir = Path("analysis_output")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / filename
        
        # Clean results to avoid circular references
        cleaned_results = self._clean_for_json(self.results)
        
        with open(output_file, 'w') as f:
            json.dump(cleaned_results, f, indent=2)
        
        self.logger.logger.info(f"Analysis results exported to {output_file}")
        
        return output_file
    
    def _clean_for_json(self, obj):
        """Clean object for JSON export."""
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
    
    def run_benchmark(self, stack_sizes=[4, 6, 8, 10, 12], iterations=2):
        """Run benchmark on different stack sizes."""
        self.logger.logger.info("Starting benchmark...")
        
        manager = StackManager()
        benchmark_results = {}
        
        for size in stack_sizes:
            self.logger.logger.info(f"Benchmarking stack size {size}...")
            
            size_results = []
            
            for i in range(iterations):
                stack = manager.generate_random_stack(size)
                result = self.analyze_game(stack, algorithm="both", depth_limit=None)
                size_results.append(result)
            
            # Calculate averages
            if size_results:
                avg_minimax_nodes = sum(r.get("minimax", {}).get("statistics", {}).get("nodes_evaluated", 0) 
                                       for r in size_results) / len(size_results)
                avg_alphabeta_nodes = sum(r.get("alphabeta", {}).get("summary", {}).get("nodes_evaluated", 0) 
                                         for r in size_results) / len(size_results)
                avg_speedup = avg_minimax_nodes / avg_alphabeta_nodes if avg_alphabeta_nodes > 0 else 0
                
                benchmark_results[size] = {
                    "stack_size": size,
                    "avg_minimax_nodes": avg_minimax_nodes,
                    "avg_alphabeta_nodes": avg_alphabeta_nodes,
                    "avg_speedup": avg_speedup,
                    "iterations": iterations
                }
        
        self.results["benchmark"] = benchmark_results
        
        # Generate benchmark report
        self._generate_benchmark_report(benchmark_results)
        
        return benchmark_results
    
    def _generate_benchmark_report(self, benchmark_results):
        """Generate benchmark report."""
        report = []
        report.append("=" * 80)
        report.append("BENCHMARK REPORT")
        report.append("=" * 80)
        report.append(f"{'Stack Size':>12} {'Minimax Nodes':>15} {'Alpha-Beta Nodes':>15} {'Speedup':>10}")
        report.append("-" * 80)
        
        for size, results in benchmark_results.items():
            report.append(f"{size:>12} {results['avg_minimax_nodes']:>15,.0f} "
                         f"{results['avg_alphabeta_nodes']:>15,.0f} {results['avg_speedup']:>10.2f}x")
        
        report_text = "\n".join(report)
        print(report_text)
        
        # Save to file
        output_file = Path("analysis_output") / "benchmark_report.txt"
        with open(output_file, 'w') as f:
            f.write(report_text)
        
        return report_text


def run_fixed_analysis():
    """Run fixed comprehensive analysis."""
    print("\n" + "=" * 80)
    print("STACK-BASED 21 SOLVER - FIXED COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
    # Create analyzer
    analyzer = FixedGameAnalyzer(log_level="INFO")
    
    # Example 1: Analyze specific games
    print("\n" + "=" * 80)
    print("EXAMPLE 1: SPECIFIC GAME ANALYSIS")
    print("=" * 80)
    
    test_stacks = {
        "simple": [3, 5, 2, 6],
        "winning": [6, 6, 3, 2, 4, 1, 5, 3],  # Can reach 21
        "balanced": [1, 6, 2, 5, 3, 4, 1, 6, 2, 5]
    }
    
    for name, stack in test_stacks.items():
        print(f"\nAnalyzing {name} stack: {stack}")
        results = analyzer.analyze_game(stack, algorithm="both")
        
        minimax_value = results.get("minimax", {}).get("value", 0)
        alphabeta_value = results.get("alphabeta", {}).get("value", 0)
        
        print(f"  Minimax value: {minimax_value:.1f}")
        print(f"  Alpha-beta value: {alphabeta_value:.1f}")
        print(f"  Values match: {abs(minimax_value - alphabeta_value) < 0.001}")
        
        if "comparison" in results:
            comp = results["comparison"]
            print(f"  Speedup: {comp.get('speedup_factor', 0):.2f}x")
            print(f"  Pruning efficiency: {comp.get('pruning_efficiency', 0):.2%}")
    
    # Example 2: Run benchmark
    print("\n" + "=" * 80)
    print("EXAMPLE 2: BENCHMARK")
    print("=" * 80)
    
    benchmark_results = analyzer.run_benchmark(stack_sizes=[4, 6, 8], iterations=2)
    
    # Example 3: Strategic analysis
    print("\n" + "=" * 80)
    print("EXAMPLE 3: STRATEGIC ANALYSIS")
    print("=" * 80)
    
    print("\nCritical positions analysis:")
    print("  Positions where player can force win by reaching 21:")
    for total in range(15, 22):
        for move in range(1, 7):
            if total + move == 21:
                print(f"    Total {total}: taking {move} wins")
                break
    
    # Export results
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    export_file = analyzer.export_results()
    print(f"Results exported to: {export_file}")
    
    # Save log analysis
    log_file = analyzer.logger.save_log_analysis("fixed_analysis_log.json")
    print(f"Log analysis saved to: {log_file}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    
    return analyzer.results


if __name__ == "__main__":
    try:
        results = run_fixed_analysis()
        
        print("\nGenerated files:")
        print("  • analysis_output/fixed_analysis_results.json - Analysis data")
        print("  • analysis_output/benchmark_report.txt - Benchmark results")
        print("  • logs/fixed_analysis_log.json - Detailed logs")
        
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()