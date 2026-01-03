import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.game_state import GameState
from src.algorithms.minimax import MinimaxSolver
from src.algorithms.alphabeta import alphabeta_with_tracking, AlphaBetaSolver
from src.algorithms.solution_tracker import SolutionTracker


def debug_simple_game():
    """Test with a very simple game that should have a clear solution."""
    print("=" * 70)
    print("DEBUG: SIMPLE GAME TEST")
    print("=" * 70)
    
    # Test 1: Simple stack where first move should lead to win
    stack = [6, 6, 3, 2]  # Take 6 -> total=6, then opponent takes 6 -> total=12, then take 3 -> total=15, etc.
    
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    print(f"Stack: {stack}")
    print(f"Initial total: {initial_state.total}")
    print(f"Initial player: {'MAX' if initial_state.is_maximizing else 'MIN'}")
    print(f"Possible moves: {initial_state.get_possible_moves()}")
    print()
    
    # Test minimax
    print("Testing Minimax:")
    minimax_solver = MinimaxSolver()
    minimax_value, minimax_best = minimax_solver.solve(initial_state)
    print(f"  Value: {minimax_value}")
    print(f"  Best move: {minimax_best.move_from_parent if minimax_best else 'None'}")
    print(f"  Nodes evaluated: {minimax_solver.nodes_evaluated}")
    print(f"  Max depth: {minimax_solver.max_depth_reached}")
    print()
    
    # Test alpha-beta
    print("Testing Alpha-Beta:")
    tracker = SolutionTracker()
    alphabeta_value, alphabeta_terminal = alphabeta_with_tracking(
        initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
        is_maximizing=True, tracker=tracker, depth_limit=None
    )
    print(f"  Value: {alphabeta_value}")
    print(f"  Nodes evaluated: {tracker.nodes_evaluated}")
    print(f"  Branches pruned: {tracker.pruned_branches}")
    
    # Try to reconstruct path
    path = tracker.reconstruct_solution_path(initial_state, alphabeta_terminal)
    if path:
        print(f"  Solution path length: {len(path)}")
        print(f"  Final total: {path[-1].total if path else 'N/A'}")
        print()
        print("  Move sequence:")
        for i, state in enumerate(path):
            if i == 0:
                print(f"    Turn 0: Initial state, total={state.total}")
            else:
                move = state.move_from_parent
                print(f"    Turn {i}: Take {move[0]}, discard {move[1]} -> total={state.total}")
    
    return initial_state, minimax_solver, tracker


def debug_game_state():
    """Test GameState functionality."""
    print("\n" + "=" * 70)
    print("DEBUG: GAME STATE TEST")
    print("=" * 70)
    
    stack = [3, 5, 2, 6]
    state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    print(f"Initial state:")
    print(f"  Total: {state.total}")
    print(f"  Stack index: {state.stack_index}")
    print(f"  Is terminal: {state.is_terminal}")
    print(f"  Evaluation: {state.evaluate()}")
    print(f"  Possible moves: {state.get_possible_moves()}")
    print()
    
    # Apply a move
    moves = state.get_possible_moves()
    if moves:
        child = state.apply_move(moves[0])
        print(f"After taking {moves[0][0]}, discarding {moves[0][1]}:")
        print(f"  Total: {child.total}")
        print(f"  Stack index: {child.stack_index}")
        print(f"  Is terminal: {child.is_terminal}")
        print(f"  Player to move: {'MAX' if child.is_maximizing else 'MIN'}")
        print(f"  Parent exists: {child.parent is not None}")
        print(f"  Move from parent: {child.move_from_parent}")
    
    return state


def debug_terminal_states():
    """Test terminal state detection."""
    print("\n" + "=" * 70)
    print("DEBUG: TERMINAL STATE TEST")
    print("=" * 70)
    
    # Test exact 21
    state1 = GameState(total=21, stack_index=0, stack=[1, 2], is_maximizing=True)
    print(f"Total=21: is_terminal={state1.is_terminal}, eval={state1.evaluate()}")
    
    # Test over 21
    state2 = GameState(total=22, stack_index=0, stack=[1, 2], is_maximizing=True)
    print(f"Total=22: is_terminal={state2.is_terminal}, eval={state2.evaluate()}")
    
    # Test stack exhausted
    state3 = GameState(total=10, stack_index=2, stack=[1, 2], is_maximizing=True)
    print(f"Stack exhausted: is_terminal={state3.is_terminal}, eval={state3.evaluate()}")
    
    # Test normal state
    state4 = GameState(total=10, stack_index=0, stack=[1, 2, 3, 4], is_maximizing=True)
    print(f"Normal state: is_terminal={state4.is_terminal}, eval={state4.evaluate()}")


def debug_performance():
    """Test algorithm performance on different stack sizes."""
    print("\n" + "=" * 70)
    print("DEBUG: PERFORMANCE TEST")
    print("=" * 70)
    
    import time
    
    test_stacks = [
        ([3, 5, 2, 6], "Simple 4"),
        ([1, 2, 3, 4, 5, 6], "Medium 6"),
        ([6, 1, 5, 2, 4, 3, 6, 1], "Complex 8"),
    ]
    
    for stack, name in test_stacks:
        print(f"\nTesting {name} (stack: {stack}):")
        
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        # Minimax
        start = time.time()
        minimax_solver = MinimaxSolver()
        minimax_value, _ = minimax_solver.solve(initial_state)
        minimax_time = time.time() - start
        
        # Alpha-beta
        start = time.time()
        tracker = SolutionTracker()
        alphabeta_value, _ = alphabeta_with_tracking(
            initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=True, tracker=tracker, depth_limit=None
        )
        alphabeta_time = time.time() - start
        
        print(f"  Minimax: {minimax_time:.4f}s, {minimax_solver.nodes_evaluated} nodes")
        print(f"  Alpha-beta: {alphabeta_time:.4f}s, {tracker.nodes_evaluated} nodes")
        print(f"  Speedup: {minimax_time/alphabeta_time:.2f}x")
        print(f"  Values match: {abs(minimax_value - alphabeta_value) < 0.001}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STACK-BASED 21 SOLVER - DEBUG TESTS")
    print("=" * 70)
    
    try:
        # Run debug tests
        state1 = debug_game_state()
        debug_terminal_states()
        initial_state, minimax_solver, tracker = debug_simple_game()
        debug_performance()
        
        print("\n" + "=" * 70)
        print("DEBUG TESTS COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nError during debug: {e}")
        import traceback
        traceback.print_exc()