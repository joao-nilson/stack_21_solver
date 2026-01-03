import sys
import os
import json
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.stack_manager import StackManager
from src.game.game_state import GameState
from src.algorithms.minimax import MinimaxSolver
from src.algorithms.alphabeta import AlphaBetaSolver
from src.algorithms.solution_tracker import SolutionTracker
from src.visualization.path_visualizer import PathVisualizer
from src.visualization.tree_visualizer import TreeVisualizer


class SolutionPathDemo:

    def __init__(self):
        self.stacks = {}
        self.heuristics = {}
        self.results = {}
        
    def load_sample_stacks(self):
        # Load from sample_stacks.json if exists
        sample_file = Path("data") / "sample_stacks.json"
        if sample_file.exists():
            with open(sample_file, 'r') as f:
                data = json.load(f)
                sample_stacks = data.get("sample_stacks", {})
                
                for name, info in sample_stacks.items():
                    self.stacks[name] = info["stack"]
        else:
            # Create sample stacks
            manager = StackManager()
            self.stacks = {
                "simple_short": [3, 5, 2, 6],
                "winning_pattern": [6, 1, 5, 2, 4, 3, 3, 4, 2, 5, 1, 6],
                "balanced_medium": manager.generate_balanced_stack(10),
                "biased_high": [6, 6, 5, 5, 6, 4, 6, 3],
                "biased_low": [1, 1, 2, 2, 1, 3, 1, 4],
                "alternating": [1, 6, 2, 5, 3, 4, 4, 3, 5, 2],
                "increasing": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
                "challenge": [6, 2, 5, 3, 4, 1, 6, 2, 5, 3, 4, 1]
            }
        
        print(f"Loaded {len(self.stacks)} sample stacks")
        return self.stacks
    
    def define_heuristics(self):
        
        def heuristic_closeness(state):
            if state.total == 21:
                return 10000 if state.is_maximizing else -10000
            if state.total > 21:
                return -10000 if state.is_maximizing else 10000
            
            distance = 21 - state.total
            score = 1000 - (distance * 50)
            return score if state.is_maximizing else -score
        
        def heuristic_aggressive(state):
            if state.total == 21:
                return 10000 if state.is_maximizing else -10000
            if state.total > 21:
                return -10000 if state.is_maximizing else 10000
            
            score = state.total * 100
            if 15 <= state.total <= 20:
                score += (state.total - 14) * 500
            return score if state.is_maximizing else -score
        
        def heuristic_cautious(state):
            if state.total == 21:
                return 10000 if state.is_maximizing else -10000
            if state.total > 21:
                return -50000 if state.is_maximizing else 50000
            
            remaining_to_bust = 21 - state.total
            if remaining_to_bust < 4: 
                score = state.total * 10 
            else:
                score = state.total * 50 
            
            return score if state.is_maximizing else -score
        
        def heuristic_balanced(state):
            if state.total == 21:
                return 10000 if state.is_maximizing else -10000
            if state.total > 21:
                return -10000 if state.is_maximizing else 10000
            
            # Consider remaining stack
            remaining = state.stack[state.stack_index:] if state.stack_index < len(state.stack) else []
            remaining_pairs = len(remaining) // 2
            
            avg_value = sum(remaining) / len(remaining) if remaining else 3.5
            
            projected = state.total + (remaining_pairs * avg_value)
            
            if projected <= 21:
                score = (1000 - (21 - projected) * 20) + (state.total * 10)
            else:
                overshoot = projected - 21
                score = -1000 - (overshoot * 100)
            
            return score if state.is_maximizing else -score
        
        self.heuristics = {
            "closeness": heuristic_closeness,
            "aggressive": heuristic_aggressive,
            "cautious": heuristic_cautious,
            "balanced": heuristic_balanced
        }
        
        print(f"Defined {len(self.heuristics)} heuristics")
        return self.heuristics
    
    def run_demo(self, stack_name, algorithm="alphabeta", heuristic="closeness", depth_limit=None):
        print(f"\n{'='*80}")
        print(f"DEMO: {stack_name.upper()} with {heuristic.upper()} heuristic")
        print(f"{'='*80}")
        
        stack = self.stacks.get(stack_name)
        if not stack:
            print(f"Stack '{stack_name}' not found!")
            return None
        
        heuristic_func = self.heuristics.get(heuristic)
        if not heuristic_func:
            print(f"Heuristic '{heuristic}' not found!")
            return None
        
        print(f"Stack: {stack}")
        print(f"Length: {len(stack)}, Sum: {sum(stack)}, Avg: {sum(stack)/len(stack):.2f}")
        
        initial_state = self.create_state_with_heuristic(stack, heuristic_func)
        
        if algorithm.lower() == "minimax":
            result = self.run_minimax(initial_state, depth_limit)
        else:
            result = self.run_alphabeta(initial_state, depth_limit)
        
        self.display_results(result)
        
        self.save_visualizations(result, stack_name, heuristic, algorithm)
        
        return result
    
    def create_state_with_heuristic(self, stack, heuristic_func):
        class CustomGameState(GameState):
            def evaluate(self):
                return heuristic_func(self)
        
        return CustomGameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    def run_minimax(self, initial_state, depth_limit):
        print(f"\nRunning Minimax (depth limit: {depth_limit})...")
        
        solver = MinimaxSolver(depth_limit=depth_limit)
        start_time = os.times().elapsed
        value, best_child = solver.solve(initial_state)
        exec_time = os.times().elapsed - start_time
        
        path = solver.find_optimal_path(initial_state)
        
        return {
            "algorithm": "minimax",
            "value": value,
            "execution_time": exec_time,
            "path": path,
            "statistics": solver.get_statistics(),
            "initial_state": initial_state
        }
    
    def run_alphabeta(self, initial_state, depth_limit):
        print(f"\nRunning Alpha-Beta Pruning (depth limit: {depth_limit})...")
        
        solver = AlphaBetaSolver(depth_limit=depth_limit)
        start_time = os.times().elapsed
        value, terminal_state = solver.solve(initial_state)
        exec_time = os.times().elapsed - start_time
        
        path = solver.get_solution_path(initial_state)
        
        return {
            "algorithm": "alphabeta",
            "value": value,
            "execution_time": exec_time,
            "path": path,
            "statistics": solver.get_statistics(),
            "initial_state": initial_state
        }
    
    def display_results(self, result):
        if not result:
            return
        
        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}")
        
        path = result.get("path", [])
        if not path:
            print("No solution path found!")
            return
        
        terminal_state = path[-1] if path else None
        
        print(f"Algorithm: {result.get('algorithm', 'N/A')}")
        print(f"Optimal value: {result.get('value', 'N/A'):.1f}")
        print(f"Execution time: {result.get('execution_time', 0):.4f}s")
        print(f"Path length: {len(path)} states")
        print(f"Total moves: {len(path) - 1}")
        print(f"Final total: {terminal_state.total if terminal_state else 'N/A'}")
        
        stats = result.get("statistics", {})
        if stats:
            print(f"\nStatistics:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
        
        print(f"\n{'='*60}")
        print("MOVE SEQUENCE")
        print(f"{'='*60}")
        
        for i, state in enumerate(path):
            if i == 0:
                print(f"Start: total={state.total}, player=MAX")
            else:
                move = state.move_from_parent
                player = "MAX" if not state.is_maximizing else "MIN"
                terminal_mark = " [TERMINAL]" if state.is_terminal else ""
                print(f"Move {i}: {player} takes {move[0]}, discards {move[1]} → total={state.total}{terminal_mark}")
        
        self.analyze_game_result(path)
    
    def analyze_game_result(self, path):
        if not path:
            return
        
        terminal_state = path[-1]
        
        print(f"\n{'='*60}")
        print("ANALYSIS")
        print(f"{'='*60}")
        
        if terminal_state.total == 21:
            print("PERFECT WIN! Reached exactly 21!")
            winner = "MAX" if not terminal_state.is_maximizing else "MIN"
            print(f"   Winner: {winner} (player who made the last move)")
        elif terminal_state.total > 21:
            print("BUST! Exceeded 21.")
            loser = "MAX" if not terminal_state.is_maximizing else "MIN"
            winner = "MIN" if loser == "MAX" else "MAX"
            print(f"   Loser: {loser} (player who caused the bust)")
            print(f"   Winner: {winner}")
        else:
            print("Game ended with stack exhaustion.")
            print(f"   Final total: {terminal_state.total}")
            print(f"   Distance from 21: {21 - terminal_state.total}")
            
            if terminal_state.value and terminal_state.value > 0:
                print(f"   Advantage: MAX (evaluation: {terminal_state.value:.1f})")
            elif terminal_state.value and terminal_state.value < 0:
                print(f"   Advantage: MIN (evaluation: {terminal_state.value:.1f})")
            else:
                print(f"   Game is even")
        
        if len(path) > 1:
            moves = []
            for state in path[1:]:
                if state.move_from_parent:
                    moves.append(state.move_from_parent[0])  # Value taken
            
            avg_move = sum(moves) / len(moves)
            max_move = max(moves)
            min_move = min(moves)
            
            print(f"\nMove Statistics:")
            print(f"  Average value taken: {avg_move:.2f}")
            print(f"  Maximum value taken: {max_move}")
            print(f"  Minimum value taken: {min_move}")
            print(f"  Total values taken: {sum(moves)}")
    
    def save_visualizations(self, result, stack_name, heuristic, algorithm):
        if not result or "path" not in result:
            return
        
        output_dir = Path("visualizations")
        output_dir.mkdir(exist_ok=True)
        
        path = result["path"]
        
        path_viz = PathVisualizer(show_colors=False)
        filename = f"{stack_name}_{heuristic}_{algorithm}_path.json"
        path_viz.export_path_json(path, output_dir / filename)
        
        if len(path) > 0:
            tree_viz = TreeVisualizer(max_depth=3, max_children=2)
            dot_filename = f"{stack_name}_{heuristic}_{algorithm}_tree.dot"
            tree_viz.export_tree_dot(path[0], output_dir / dot_filename, path)
        
        print(f"\nVisualizations saved to: visualizations/{filename}")
        print(f"Tree visualization: visualizations/{dot_filename}")
        print(f"To convert DOT to PNG: dot -Tpng {dot_filename} -o tree.png")
    
    def run_comparative_analysis(self, stack_name="balanced_medium"):
        print(f"\n{'='*80}")
        print(f"COMPARATIVE ANALYSIS: {stack_name.upper()}")
        print(f"{'='*80}")
        
        stack = self.stacks.get(stack_name)
        if not stack:
            print(f"Stack '{stack_name}' not found!")
            return
        
        print(f"Using stack: {stack}")
        
        results = {}
        
        for heuristic_name in self.heuristics.keys():
            print(f"\n{'─'*60}")
            print(f"Testing heuristic: {heuristic_name}")
            print(f"{'─'*60}")
            
            result = self.run_demo(stack_name, algorithm="alphabeta", 
                                  heuristic=heuristic_name, depth_limit=5)
            results[heuristic_name] = result
        
        self.generate_comparison_report(results, stack_name)
    
    def generate_comparison_report(self, results, stack_name):
        print(f"\n{'='*80}")
        print(f"HEURISTIC COMPARISON REPORT: {stack_name}")
        print(f"{'='*80}")
        
        print(f"{'Heuristic':<15} {'Value':<10} {'Time (s)':<10} {'Moves':<8} {'Final Total':<12} {'Nodes':<10}")
        print(f"{'-'*70}")
        
        for heuristic_name, result in results.items():
            if not result:
                continue
            
            path = result.get("path", [])
            terminal_state = path[-1] if path else None
            
            stats = result.get("statistics", {})
            nodes = stats.get("nodes_evaluated", 0) if isinstance(stats, dict) else 0
            
            print(f"{heuristic_name:<15} "
                  f"{result.get('value', 0):<10.1f} "
                  f"{result.get('execution_time', 0):<10.4f} "
                  f"{len(path)-1 if path else 0:<8} "
                  f"{terminal_state.total if terminal_state else 'N/A':<12} "
                  f"{nodes:<10,}")
        
        # Analysis
        print(f"\n{'='*80}")
        print("ANALYSIS OF HEURISTIC PERFORMANCE:")
        print(f"{'='*80}")
        
        best_total = None
        best_heuristic_total = None
        
        for heuristic_name, result in results.items():
            if not result:
                continue
            
            path = result.get("path", [])
            if not path:
                continue
            
            final_total = path[-1].total
            distance = abs(21 - final_total)
            
            if best_total is None or distance < best_total:
                best_total = distance
                best_heuristic_total = heuristic_name
        
        if best_heuristic_total:
            print(f"Best final total (closest to 21): {best_heuristic_total}")
        
        fastest_time = None
        fastest_heuristic = None
        
        for heuristic_name, result in results.items():
            if not result:
                continue
            
            time_taken = result.get("execution_time", float('inf'))
            if fastest_time is None or time_taken < fastest_time:
                fastest_time = time_taken
                fastest_heuristic = heuristic_name
        
        if fastest_heuristic:
            print(f"Fastest execution: {fastest_heuristic} ({fastest_time:.4f}s)")
        
        self.save_comparison_to_file(results, stack_name)
    
    def save_comparison_to_file(self, results, stack_name):
        output_dir = Path("analysis_output")
        output_dir.mkdir(exist_ok=True)
        
        comparison_data = {
            "stack_name": stack_name,
            "stack": self.stacks.get(stack_name, []),
            "comparison_date": os.times().ctime(),
            "results": {}
        }
        
        for heuristic_name, result in results.items():
            if not result:
                continue
            
            path = result.get("path", [])
            terminal_state = path[-1] if path else None
            
            comparison_data["results"][heuristic_name] = {
                "value": result.get("value"),
                "execution_time": result.get("execution_time"),
                "path_length": len(path),
                "moves": len(path) - 1 if path else 0,
                "final_total": terminal_state.total if terminal_state else None,
                "is_21": terminal_state.total == 21 if terminal_state else False,
                "is_bust": terminal_state.total > 21 if terminal_state else False
            }
        
        filename = f"heuristic_comparison_{stack_name}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(comparison_data, f, indent=2)
        
        print(f"\nComparison saved to: {filepath}")


def main():
    print(f"\n{'='*80}")
    print("SOLUTION PATH DEMONSTRATION")
    print("Stack-based 21 with Different Heuristics")
    print(f"{'='*80}")
    
    demo = SolutionPathDemo()
    
    demo.load_sample_stacks()
    
    demo.define_heuristics()
    
    while True:
        print(f"\n{'='*80}")
        print("MAIN MENU")
        print(f"{'='*80}")
        print("1. Show available stacks")
        print("2. Show available heuristics")
        print("3. Run single demo")
        print("4. Run comparative analysis")
        print("5. Run all demonstrations")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            print("\nAvailable stacks:")
            for i, (name, stack) in enumerate(demo.stacks.items(), 1):
                print(f"{i:2}. {name:20} Length: {len(stack):2} Sum: {sum(stack):3} Avg: {sum(stack)/len(stack):.2f}")
        
        elif choice == "2":
            print("\nAvailable heuristics:")
            for i, (name, func) in enumerate(demo.heuristics.items(), 1):
                print(f"{i}. {name}")
                if "closeness" in name:
                    print("   - Focuses on closeness to 21")
                elif "aggressive" in name:
                    print("   - Aggressive, always goes for higher totals")
                elif "cautious" in name:
                    print("   - Cautious, avoids busting at all costs")
                elif "balanced" in name:
                    print("   - Balanced, considers both total and remaining stack")
        
        elif choice == "3":
            print("\nAvailable stacks:")
            stack_names = list(demo.stacks.keys())
            for i, name in enumerate(stack_names, 1):
                print(f"{i}. {name}")
            
            stack_choice = input(f"\nSelect stack (1-{len(stack_names)}): ").strip()
            try:
                stack_idx = int(stack_choice) - 1
                if 0 <= stack_idx < len(stack_names):
                    stack_name = stack_names[stack_idx]
                else:
                    print("Invalid choice!")
                    continue
            except ValueError:
                print("Invalid input!")
                continue
            
            print("\nAvailable heuristics:")
            heuristic_names = list(demo.heuristics.keys())
            for i, name in enumerate(heuristic_names, 1):
                print(f"{i}. {name}")
            
            heuristic_choice = input(f"\nSelect heuristic (1-{len(heuristic_names)}): ").strip()
            try:
                heuristic_idx = int(heuristic_choice) - 1
                if 0 <= heuristic_idx < len(heuristic_names):
                    heuristic_name = heuristic_names[heuristic_idx]
                else:
                    print("Invalid choice!")
                    continue
            except ValueError:
                print("Invalid input!")
                continue
            
            algorithm = input("\nSelect algorithm (minimax/alphabeta) [alphabeta]: ").strip().lower()
            if not algorithm:
                algorithm = "alphabeta"
            
            depth_input = input("\nDepth limit (press Enter for unlimited): ").strip()
            depth_limit = int(depth_input) if depth_input else None
            
            demo.run_demo(stack_name, algorithm, heuristic_name, depth_limit)
        
        elif choice == "4":
            print("\nAvailable stacks for comparative analysis:")
            stack_names = list(demo.stacks.keys())
            for i, name in enumerate(stack_names, 1):
                print(f"{i}. {name}")
            
            stack_choice = input(f"\nSelect stack (1-{len(stack_names)}): ").strip()
            try:
                stack_idx = int(stack_choice) - 1
                if 0 <= stack_idx < len(stack_names):
                    stack_name = stack_names[stack_idx]
                else:
                    print("Invalid choice!")
                    continue
            except ValueError:
                print("Invalid input!")
                continue
            
            demo.run_comparative_analysis(stack_name)
        
        elif choice == "5":
            print("\nRunning all demonstrations...")
            
            # Run demos for key configurations
            key_configurations = [
                ("simple_short", "closeness", "alphabeta"),
                ("winning_pattern", "aggressive", "alphabeta"),
                ("balanced_medium", "balanced", "alphabeta"),
                ("biased_high", "cautious", "alphabeta"),
                ("challenge", "balanced", "minimax"),
            ]
            
            for stack_name, heuristic, algorithm in key_configurations:
                if stack_name in demo.stacks and heuristic in demo.heuristics:
                    demo.run_demo(stack_name, algorithm, heuristic, depth_limit=5)
                else:
                    print(f"Skipping {stack_name} with {heuristic} - not available")
        
        elif choice == "6":
            print("\nExiting. Goodbye!")
            break
        
        else:
            print("\nInvalid choice! Please enter 1-6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()