# tree_viz_example.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.game_state import GameState
from src.visualization.tree_visualizer import TreeVisualizer
from src.algorithms.alphabeta import AlphaBetaSolver

def visualize_game_tree():
    # Create a sample game
    print("=" * 60)
    print("TREE VISUALIZATION DEMO")
    print("=" * 60)
    
    # Define different stacks to visualize
    games = {
        "Simple Game": [3, 5, 2, 6],
        "Balanced Game": [1, 6, 2, 5, 3, 4, 1, 6],
        "Risky Game": [6, 6, 5, 5, 6, 4]
    }
    
    for name, stack in games.items():
        print(f"\n{'='*60}")
        print(f"VISUALIZING: {name}")
        print(f"Stack: {stack}")
        print(f"{'='*60}")
        
        # Create game state
        initial_state = GameState(
            total=0,
            stack_index=0,
            stack=stack,
            is_maximizing=True
        )
        
        # Solve to get optimal path
        solver = AlphaBetaSolver(depth_limit=5)
        value, terminal_state = solver.solve(initial_state)
        path = solver.get_solution_path(initial_state)
        
        # Create visualizer
        visualizer = TreeVisualizer(max_depth=3, max_children=2)
        
        # Generate visualization
        tree_text = visualizer.visualize_tree(initial_state, highlight_path=path)
        print(tree_text)
        
        # Export to DOT file
        dot_filename = f"{name.lower().replace(' ', '_')}_tree.dot"
        visualizer.export_tree_dot(initial_state, dot_filename, path)
        print(f"✓ Tree exported to: {dot_filename}")
        print(f"  Convert to PNG: dot -Tpng {dot_filename} -o tree.png")

def compare_different_visualizations():
    """Compare different visualization settings"""
    print("\n" + "="*60)
    print("COMPARING VISUALIZATION SETTINGS")
    print("="*60)
    
    stack = [3, 5, 2, 6, 4, 1]
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    solver = AlphaBetaSolver(depth_limit=4)
    value, terminal_state = solver.solve(initial_state)
    path = solver.get_solution_path(initial_state)
    
    # Test different settings
    settings = [
        ("Shallow tree", {"max_depth": 2, "max_children": 2}),
        ("Deep tree", {"max_depth": 4, "max_children": 2}),
        ("Wide tree", {"max_depth": 3, "max_children": 4}),
        ("Detailed view", {"max_depth": 3, "max_children": 2, "width": 120})
    ]
    
    for name, params in settings:
        print(f"\n{'-'*40}")
        print(f"{name.upper()}")
        print(f"{'-'*40}")
        
        visualizer = TreeVisualizer(**params)
        tree_text = visualizer.visualize_tree(initial_state, highlight_path=path)
        
        # Show just the beginning
        lines = tree_text.split('\n')
        for i in range(min(15, len(lines))):
            print(lines[i])
        
        if len(lines) > 15:
            print("... (output truncated)")

def interactive_visualization():
    """Interactive mode for exploring trees"""
    print("\n" + "="*60)
    print("INTERACTIVE TREE VISUALIZATION")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Enter custom stack (e.g., '3,5,2,6,4,1')")
        print("2. Use predefined stack")
        print("3. Adjust visualization settings")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            stack_str = input("Enter stack values (comma-separated): ").strip()
            try:
                stack = [int(x.strip()) for x in stack_str.split(',')]
                if len(stack) < 4:
                    print("Stack must have at least 4 values")
                    continue
                    
                visualize_single_game(stack)
                
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")
                
        elif choice == "2":
            predefined = {
                "1": [3, 5, 2, 6],
                "2": [1, 6, 2, 5, 3, 4, 1, 6],
                "3": [6, 6, 5, 5, 6, 4],
                "4": [1, 1, 2, 2, 3, 3, 4, 4]
            }
            
            print("\nPredefined stacks:")
            for key, values in predefined.items():
                print(f"{key}. {values}")
            
            stack_choice = input("\nSelect stack (1-4): ").strip()
            if stack_choice in predefined:
                visualize_single_game(predefined[stack_choice])
            else:
                print("Invalid choice")
                
        elif choice == "3":
            max_depth = input("Max depth (default 3): ").strip()
            max_depth = int(max_depth) if max_depth else 3
            
            max_children = input("Max children per node (default 2): ").strip()
            max_children = int(max_children) if max_children else 2
            
            visualizer = TreeVisualizer(
                max_depth=max_depth,
                max_children=max_children
            )
            print(f"Visualizer configured: depth={max_depth}, children={max_children}")
            
        elif choice == "4":
            print("Exiting interactive mode")
            break

def visualize_single_game(stack):
    """Helper function to visualize a single game"""
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    solver = AlphaBetaSolver(depth_limit=min(len(stack) // 2, 6))
    value, terminal_state = solver.solve(initial_state)
    path = solver.get_solution_path(initial_state)
    
    visualizer = TreeVisualizer(max_depth=3, max_children=2)
    tree_text = visualizer.visualize_tree(initial_state, highlight_path=path)
    print(tree_text)
    
    # Show statistics
    terminal = path[-1] if path else None
    if terminal:
        print(f"\nGame Analysis:")
        print(f"  Final total: {terminal.total}")
        print(f"  Moves: {len(path)-1}")
        print(f"  Optimal value: {value:.1f}")
        
        if terminal.total == 21:
            print(f"  Result: WIN! (Reached exactly 21)")
        elif terminal.total > 21:
            print(f"  Result: BUST! (Exceeded 21)")
        else:
            print(f"  Result: Stack exhausted at {terminal.total}")

if __name__ == "__main__":
    try:
        # Run the demos
        visualize_game_tree()
        compare_different_visualizations()
        
        # Uncomment to enable interactive mode
        # interactive_visualization()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
