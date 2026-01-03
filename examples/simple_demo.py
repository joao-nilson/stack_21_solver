import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.stack_manager import StackManager
from src.game.game_state import GameState
from src.algorithms.minimax import MinimaxSolver
from src.algorithms.alphabeta import alphabeta_with_tracking
from src.algorithms.solution_tracker import SolutionTracker
from src.visualization.path_visualizer import PathVisualizer
from src.utils.performance import PerformanceMonitor


def demo_minimax_basic():
    print("=" * 70)
    print("MINIMAX DEMONSTRATION")
    print("=" * 70)
    
    stack = [3, 5, 2, 6]
    print(f"Stack: {stack}")
    print(f"Stack length: {len(stack)}")
    print()
    
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    solver = MinimaxSolver(depth_limit=None)
    print("Running minimax algorithm...")
    
    value, best_child = solver.solve(initial_state)
    
    print(f"\nResults:")
    print(f"  Optimal value: {value}")
    print(f"  Best first move: Take {best_child.move_from_parent[0]} (discard {best_child.move_from_parent[1]})")
    print(f"  Resulting total: {best_child.total}")
    
    stats = solver.get_statistics()
    print(f"\nStatistics:")
    print(f"  Nodes evaluated: {stats['nodes_evaluated']}")
    print(f"  Max depth reached: {stats['max_depth_reached']}")
    print(f"  Execution time: {stats['execution_time_seconds']:.4f} seconds")
    print(f"  Nodes per second: {stats['nodes_per_second']:,.0f}")
    
    return initial_state, solver


def demo_alphabeta_with_tracking():
    print("\n" + "=" * 70)
    print("ALPHA-BETA PRUNING DEMONSTRATION")
    print("=" * 70)
    
    stack = [3, 5, 2, 6, 4, 1, 3, 2]
    print(f"Stack: {stack}")
    print(f"Stack length: {len(stack)}")
    print()
    
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    tracker = SolutionTracker()
    
    print("Running alpha-beta pruning with solution tracking...")
    value, terminal_state = alphabeta_with_tracking(
        initial_state, 
        depth=0,
        alpha=float('-inf'),
        beta=float('inf'),
        is_maximizing=True,
        tracker=tracker,
        depth_limit=None
    )
    
    print(f"\nResults:")
    print(f"  Optimal value: {value}")
    
    path = tracker.reconstruct_solution_path(initial_state, terminal_state)
    
    if path:
        print(f"  Solution path length: {len(path)} states")
        print(f"  Total moves: {len(path) - 1}")
        print(f"  Final total: {path[-1].total}")
        
        summary = tracker.get_solution_summary()
        if summary:
            print(f"\nSolution Summary:")
            print(f"  Winning player: {summary['winning_player']}")
            print(f"  Nodes evaluated: {summary['nodes_evaluated']}")
            print(f"  Branches pruned: {summary['pruned_branches']}")
            print(f"  Pruning efficiency: {summary['pruning_efficiency']:.2%}")
    
    return initial_state, tracker, path


def demo_path_visualization(path):
    print("\n" + "=" * 70)
    print("SOLUTION PATH VISUALIZATION")
    print("=" * 70)
    
    if not path:
        print("No solution path to visualize.")
        return
    
    visualizer = PathVisualizer(show_colors=True)
    
    visualization = visualizer.visualize_solution_path(path, show_details=True)
    print(visualization)
    
    visualizer.export_path_json(path, "simple_demo_solution.json")
    print(f"\nSolution exported to: simple_demo_solution.json")


def demo_performance_comparison():
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON")
    print("=" * 70)
    
    stack = [3, 5, 2, 6, 4, 1, 3, 2, 5, 4]
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    monitor_minimax = PerformanceMonitor(enabled=True)
    monitor_alphabeta = PerformanceMonitor(enabled=True)
    
    print("Testing minimax algorithm...")
    solver_minimax = MinimaxSolver(depth_limit=4)  # Limit depth for reasonable time
    
    monitor_minimax.start()
    value1, _ = solver_minimax.solve(initial_state)
    monitor_minimax.stop()
    
    stats_minimax = monitor_minimax.get_current_stats()
    stats_minimax["algorithm"] = "minimax"
    
    print("Testing alpha-beta pruning...")
    tracker = SolutionTracker()
    
    monitor_alphabeta.start()
    value2, _ = alphabeta_with_tracking(
        initial_state, 
        depth=0,
        alpha=float('-inf'),
        beta=float('inf'),
        is_maximizing=True,
        tracker=tracker,
        depth_limit=4
    )
    monitor_alphabeta.stop()
    
    stats_alphabeta = monitor_alphabeta.get_current_stats()
    stats_alphabeta["algorithm"] = "alpha-beta"
    stats_alphabeta["pruned_branches"] = tracker.pruned_branches
    
    print(f"\nComparison Results:")
    print(f"  Minimax value: {value1}")
    print(f"  Alpha-beta value: {value2}")
    print(f"  Values match: {abs(value1 - value2) < 0.001}")
    
    monitor = PerformanceMonitor()
    comparison = monitor.compare_algorithms(stats_minimax, stats_alphabeta, "Minimax", "Alpha-Beta")
    print(comparison)


def demo_interactive_move_analysis():
    print("\n" + "=" * 70)
    print("INTERACTIVE MOVE ANALYSIS")
    print("=" * 70)
    
    stack = [3, 5, 2, 6]
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    solver = MinimaxSolver(depth_limit=3)
    
    print(f"Analyzing moves from initial position (total=0):")
    moves_analysis = solver.analyze_move_quality(initial_state)
    
    for i, analysis in enumerate(moves_analysis):
        print(f"\nMove {i+1}:")
        print(f"  Take {analysis['value_taken']}, discard {analysis['value_discarded']}")
        print(f"  New total: {analysis['new_total']}")
        print(f"  Evaluation: {analysis['evaluation']:.1f}")
        print(f"  Interpretation: {analysis['interpretation']}")
    
    if moves_analysis:
        best_move = moves_analysis[0]
        child_state = best_move['child_state']
        
        print(f"\nAfter best move (total={child_state.total}):")
        print(f"  Next player: {'MIN' if child_state.is_maximizing else 'MAX'}")
        print(f"  Remaining stack: {child_state.stack[child_state.stack_index:]}")
        
        if not child_state.is_terminal:
            next_moves_analysis = solver.analyze_move_quality(child_state)
            print(f"  Next player has {len(next_moves_analysis)} possible moves")


def demo_stack_analysis():
    print("\n" + "=" * 70)
    print("STACK ANALYSIS")
    print("=" * 70)
    
    manager = StackManager()
    
    stacks = {
        "Random": manager.generate_random_stack(10),
        "Balanced": manager.generate_balanced_stack(12),
        "Biased (6s)": manager.generate_biased_stack(10, bias_value=6, bias_factor=0.7),
        "Test Stack": [1, 2, 3, 4, 5, 6, 1, 2, 3, 4]
    }
    
    for name, stack in stacks.items():
        print(f"\n{name} Stack: {stack}")
        analysis = manager.analyze_stack(stack)
        
        print(f"  Length: {analysis['length']}")
        print(f"  Sum: {analysis['sum']}")
        print(f"  Average: {analysis['average']:.2f}")
        print(f"  Min/Max: {analysis['min']}/{analysis['max']}")
        print(f"  Distribution: {analysis['value_distribution']}")
        print(f"  Expected moves: {analysis['expected_moves']}")


def main():
    print("\n" + "=" * 70)
    print("STACK-BASED 21 SOLVER - SIMPLE DEMONSTRATION")
    print("=" * 70)
    
    try:
        # Demo 1: Basic minimax
        initial_state_minimax, minimax_solver = demo_minimax_basic()
        
        # Demo 2: Alpha-beta with tracking
        initial_state_ab, tracker, path = demo_alphabeta_with_tracking()
        
        # Demo 3: Path visualization
        demo_path_visualization(path)
        
        # Demo 4: Performance comparison
        demo_performance_comparison()
        
        # Demo 5: Interactive move analysis
        demo_interactive_move_analysis()
        
        # Demo 6: Stack analysis
        demo_stack_analysis()
        
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("\nCheck the following files:")
        print("  • simple_demo_solution.json - Solution path export")
        print("  • logs/ - Performance logs and analysis")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()