#examples/path_vizualization_demo.py
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.stack_manager import StackManager
from src.game.game_state import GameState
from src.algorithms.alphabeta import AlphaBetaSolver
from src.visualization.path_visualizer import PathVisualizer
from src.visualization.tree_visualizer import TreeVisualizer


class InteractivePathVisualizer:
    
    def __init__(self):
        self.stacks = {}
        self.current_result = None
        self.load_stacks()
    
    def load_stacks(self):
        manager = StackManager()
        
        self.stacks = {
            "quick_game": [3, 5, 2, 6],
            "balanced": manager.generate_balanced_stack(8),
            "high_risk": [6, 6, 5, 5, 6, 4],
            "low_risk": [1, 2, 2, 3, 3, 4],
            "challenge": [6, 2, 5, 3, 4, 1, 6, 2],
            "pattern": [1, 6, 2, 5, 3, 4, 4, 3],
            "extreme": [6, 1, 6, 1, 6, 1, 6, 1]
        }
    
    def solve_game(self, stack_name):
        if stack_name not in self.stacks:
            print(f"Stack '{stack_name}' not found!")
            return False
        
        stack = self.stacks[stack_name]
        print(f"\nSolving game with stack: {stack}")
        
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        solver = AlphaBetaSolver(depth_limit=None)
        
        value, terminal_state = solver.solve(initial_state)
        path = solver.get_solution_path(initial_state)
        
        self.current_result = {
            "stack_name": stack_name,
            "stack": stack,
            "value": value,
            "path": path,
            "terminal_state": terminal_state,
            "statistics": solver.get_statistics(),
            "initial_state": initial_state
        }
        
        print(f"Solution found! Value: {value}, Path length: {len(path)}")
        return True
    
    def display_path_text(self):
        if not self.current_result:
            print("No result to display!")
            return
        
        path = self.current_result["path"]
        visualizer = PathVisualizer(show_colors=True)
        
        visualization = visualizer.visualize_solution_path(path, show_details=True)
        print(visualization)
    
    def display_path_json(self):
        if not self.current_result:
            print("No result to display!")
            return
        
        path = self.current_result["path"]
        visualizer = PathVisualizer(show_colors=False)
        
        # Export to temporary file
        temp_file = Path("temp_path.json")
        visualizer.export_path_json(path, temp_file)
        
        # Read and display
        with open(temp_file, 'r') as f:
            data = json.load(f)
        
        print(json.dumps(data, indent=2))
        temp_file.unlink()  # Clean up
    
    def display_tree(self, max_depth=3):
        if not self.current_result:
            print("No result to display!")
            return
        
        initial_state = self.current_result["initial_state"]
        path = self.current_result["path"]
        
        visualizer = TreeVisualizer(max_depth=max_depth, max_children=2)
        tree_text = visualizer.visualize_tree(initial_state, path)
        
        print(tree_text)
    
    def export_tree_dot(self):
        if not self.current_result:
            print("No result to display!")
            return
        
        initial_state = self.current_result["initial_state"]
        path = self.current_result["path"]
        
        visualizer = TreeVisualizer()
        filename = f"{self.current_result['stack_name']}_tree.dot"
        visualizer.export_tree_dot(initial_state, filename, path)
        
        print(f"Tree exported to: {filename}")
        print(f"Convert to PNG: dot -Tpng {filename} -o tree.png")
    
    def analyze_moves(self):
        if not self.current_result:
            print("No result to analyze!")
            return
        
        path = self.current_result["path"]
        
        print(f"\n{'='*60}")
        print("MOVE ANALYSIS")
        print(f"{'='*60}")
        
        # Collect move statistics
        moves_taken = []
        moves_discarded = []
        
        for i, state in enumerate(path[1:], 1):
            if state.move_from_parent:
                taken, discarded, _ = state.move_from_parent
                moves_taken.append(taken)
                moves_discarded.append(discarded)
                
                player = "MAX" if not state.is_maximizing else "MIN"
                print(f"Move {i}: {player} takes {taken} (discards {discarded})")
        
        if moves_taken:
            print(f"\nStatistics:")
            print(f"  Moves taken: {len(moves_taken)}")
            print(f"  Average value taken: {sum(moves_taken)/len(moves_taken):.2f}")
            print(f"  Total value taken: {sum(moves_taken)}")
            print(f"  Max value taken: {max(moves_taken)}")
            print(f"  Min value taken: {min(moves_taken)}")
            print(f"  Average value discarded: {sum(moves_discarded)/len(moves_discarded):.2f}")
    
    def compare_with_alternative(self):
        if not self.current_result:
            print("No result to compare!")
            return
        
        initial_state = self.current_result["initial_state"]
        stack_name = self.current_result["stack_name"]
        
        print(f"\n{'='*60}")
        print("ALTERNATIVE MOVE ANALYSIS")
        print(f"{'='*60}")
        
        # Get all possible first moves
        moves = initial_state.get_possible_moves()
        print(f"Possible first moves from total=0:")
        
        solver = AlphaBetaSolver(depth_limit=4)
        
        for i, move in enumerate(moves, 1):
            child_state = initial_state.apply_move(move)
            value, _ = solver.solve(child_state)
            
            outcome = "???"
            if value > 1000:
                outcome = "WINNING"
            elif value < -1000:
                outcome = "LOSING"
            elif value > 0:
                outcome = "ADVANTAGE"
            elif value < 0:
                outcome = "DISADVANTAGE"
            else:
                outcome = "NEUTRAL"
            
            print(f"  {i}. Take {move[0]}, discard {move[1]} → Value: {value:.1f} ({outcome})")
    
    def run_interactive(self):
        print(f"\n{'='*80}")
        print("INTERACTIVE PATH VISUALIZATION DEMO")
        print(f"{'='*80}")
        
        while True:
            print(f"\n{'='*60}")
            print("MAIN MENU")
            print(f"{'='*60}")
            print("1. List available stacks")
            print("2. Solve a game")
            print("3. Display path (text)")
            print("4. Display path (JSON)")
            print("5. Display tree visualization")
            print("6. Export tree to DOT format")
            print("7. Analyze moves")
            print("8. Compare with alternative moves")
            print("9. Show current result info")
            print("0. Exit")
            
            choice = input("\nEnter choice (0-9): ").strip()
            
            if choice == "1":
                print("\nAvailable stacks:")
                for i, (name, stack) in enumerate(self.stacks.items(), 1):
                    print(f"{i:2}. {name:15} - {stack}")
            
            elif choice == "2":
                print("\nAvailable stacks:")
                stack_names = list(self.stacks.keys())
                for i, name in enumerate(stack_names, 1):
                    print(f"{i}. {name}")
                
                stack_choice = input(f"\nSelect stack (1-{len(stack_names)}): ").strip()
                try:
                    idx = int(stack_choice) - 1
                    if 0 <= idx < len(stack_names):
                        self.solve_game(stack_names[idx])
                    else:
                        print("Invalid choice!")
                except ValueError:
                    print("Invalid input!")
            
            elif choice == "3":
                self.display_path_text()
            
            elif choice == "4":
                self.display_path_json()
            
            elif choice == "5":
                depth = input("Max depth to display (default 3): ").strip()
                max_depth = int(depth) if depth else 3
                self.display_tree(max_depth)
            
            elif choice == "6":
                self.export_tree_dot()
            
            elif choice == "7":
                self.analyze_moves()
            
            elif choice == "8":
                self.compare_with_alternative()
            
            elif choice == "9":
                if self.current_result:
                    print(f"\nCurrent result:")
                    print(f"  Stack: {self.current_result['stack_name']}")
                    print(f"  Stack values: {self.current_result['stack']}")
                    print(f"  Optimal value: {self.current_result['value']:.1f}")
                    print(f"  Path length: {len(self.current_result['path'])}")
                    print(f"  Final total: {self.current_result['path'][-1].total if self.current_result['path'] else 'N/A'}")
                else:
                    print("No current result. Solve a game first!")
            
            elif choice == "0":
                print("\nExiting. Goodbye!")
                break
            
            else:
                print("\nInvalid choice!")


def main():
    visualizer = InteractivePathVisualizer()
    visualizer.run_interactive()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()