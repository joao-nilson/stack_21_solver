# examples/path_vizualization_demo.py
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
from src.visualization.solution_path_visualizer import SolutionPathTreeVisualizer



class InteractivePathVisualizer:

    def __init__(self):
        self.stacks = {}
        self.current_result = None
        self.load_stacks()

    def load_stacks(self):

        json_path = Path(__file__).parent.parent / "data" / "sample_stacks.json"

        if not json_path.exists():
            raise FileNotFoundError(f"Stack JSON file not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.stacks = {}

        for name, info in data["sample_stacks"].items():
            self.stacks[name] = info["stack"]

        print(f"Loaded {len(self.stacks)} stacks from {json_path}")

    def solve_game(self, stack_name):
        if stack_name not in self.stacks:
            print(f"Stack '{stack_name}' not found!")
            return False

        stack = self.stacks[stack_name]
        print(f"\nSolving game with stack: {stack}")

        initial_state = GameState(
            total=0,
            stack_index=0,
            stack=stack,
            is_maximizing=True
        )

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

        print(f"Solution found! Value: {value:.1f}, Path length: {len(path)}")
        return True

    def display_path_text(self):
        if not self.current_result:
            print("No result to display!")
            return

        visualizer = PathVisualizer(show_colors=True)
        visualization = visualizer.visualize_solution_path(
            self.current_result["path"],
            show_details=True
        )
        print(visualization)

    def display_path_json(self):
        if not self.current_result:
            print("No result to display!")
            return

        visualizer = PathVisualizer(show_colors=False)
        temp_file = Path("temp_path.json")

        visualizer.export_path_json(self.current_result["path"], temp_file)

        with open(temp_file, "r") as f:
            print(json.dumps(json.load(f), indent=2))

        temp_file.unlink()

    def display_tree(self, max_depth=3):
        if not self.current_result:
            print("No result to display!")
            return

        visualizer = TreeVisualizer(max_depth=max_depth, max_children=2)
        tree_text = visualizer.visualize_tree(
            self.current_result["initial_state"],
            self.current_result["path"]
        )
        print(tree_text)

    def export_tree_dot(self):
        if not self.current_result:
            print("No result to display!")
            return

        filename = f"{self.current_result['stack_name']}_tree.dot"
        visualizer = TreeVisualizer()

        visualizer.export_tree_dot(
            self.current_result["initial_state"],
            filename,
            self.current_result["path"]
        )

        print(f"Tree exported to: {filename}")
        print(f"Convert to PNG: dot -Tpng {filename} -o tree.png")

    def display_solution_path_tree(self):
        if not self.current_result:
            print("No result to display!")
            return

        visualizer = SolutionPathTreeVisualizer()
        tree_text = visualizer.visualize(self.current_result["path"])
        print(tree_text)

    def analyze_moves(self):
        if not self.current_result:
            print("No result to analyze!")
            return

        path = self.current_result["path"]

        print(f"\n{'=' * 60}")
        print("MOVE ANALYSIS")
        print(f"{'=' * 60}")

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
            print("\nStatistics:")
            print(f"  Moves taken: {len(moves_taken)}")
            print(f"  Average value taken: {sum(moves_taken)/len(moves_taken):.2f}")
            print(f"  Total value taken: {sum(moves_taken)}")
            print(f"  Max value taken: {max(moves_taken)}")
            print(f"  Min value taken: {min(moves_taken)}")
            print(f"  Average value discarded: {sum(moves_discarded)/len(moves_discarded):.2f}")

    def run_interactive(self):
        print(f"\n{'=' * 80}")
        print("INTERACTIVE PATH VISUALIZATION DEMO")
        print(f"{'=' * 80}")

        while True:
            print(f"\n{'=' * 60}")
            print("MAIN MENU")
            print(f"{'=' * 60}")
            print("1. List available stacks")
            print("2. Solve a game")
            print("3. Display path (text)")
            print("4. Display path (JSON)")
            print("5. Display tree visualization")
            print("6. Export tree to DOT format")
            print("7. Analyze moves")
            print("8. Show current result info")
            print("9. Display solution path (tree)")
            print("0. Exit")

            choice = input("\nEnter choice (0-9): ").strip()

            if choice == "1":
                print("\nAvailable stacks:")
                for i, (name, stack) in enumerate(self.stacks.items(), 1):
                    print(f"{i:2}. {name:20} {stack}")

            elif choice == "2":
                stack_names = list(self.stacks.keys())
                for i, name in enumerate(stack_names, 1):
                    print(f"{i}. {name}")

                try:
                    idx = int(input("\nSelect stack: ")) - 1
                    self.solve_game(stack_names[idx])
                except Exception:
                    print("Invalid choice!")

            elif choice == "3":
                self.display_path_text()

            elif choice == "4":
                self.display_path_json()

            elif choice == "5":
                depth = input("Max depth (default 3): ").strip()
                self.display_tree(int(depth) if depth else 3)

            elif choice == "6":
                self.export_tree_dot()

            elif choice == "7":
                self.analyze_moves()

            elif choice == "8":
                if self.current_result:
                    print(json.dumps({
                        "stack": self.current_result["stack_name"],
                        "value": self.current_result["value"],
                        "path_length": len(self.current_result["path"])
                    }, indent=2))
                else:
                    print("No result yet.")

            elif choice == "9":
                self.display_solution_path_tree()

            elif choice == "0":
                break

            else:
                print("Invalid choice!")


def main():
    InteractivePathVisualizer().run_interactive()


if __name__ == "__main__":
    main()
