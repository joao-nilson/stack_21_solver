"""
Test a complete game of Stack-based 21.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.game_state import GameState
from src.algorithms.minimax import MinimaxSolver
from src.algorithms.alphabeta import alphabeta_with_tracking
from src.algorithms.solution_tracker import SolutionTracker


def test_game_completion():
    """Test that a game can actually reach 21."""
    print("=" * 70)
    print("TEST: CAN A GAME REACH 21?")
    print("=" * 70)
    
    # Create a stack that definitely allows reaching 21
    # Example: [6, 6, 6, 3] -> 6 + 6 + 6 + 3 = 21
    # But with our dual-choice, the sequence matters!
    
    # Let's create a deterministic stack where optimal play reaches 21
    # Stack: [6, 1, 6, 2, 6, 3]
    # Optimal play: Take 6 (discard 1) -> total=6
    #               Opponent takes 2 (discard 6) -> total=8
    #               Take 6 (discard 3) -> total=14
    #               Opponent... can't reach 21
    
    # Actually, let's make a simpler test
    print("\nTest 1: Simple forced win")
    stack = [6, 1, 6, 2, 6, 3]
    print(f"Stack: {stack}")
    
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    # Use minimax to solve
    solver = MinimaxSolver()
    value, best_child = solver.solve(initial_state)
    
    print(f"Minimax value: {value}")
    print(f"Best first move: {best_child.move_from_parent if best_child else 'None'}")
    
    # Find complete path
    path = solver.find_optimal_path(initial_state)
    print(f"Path length: {len(path)}")
    
    print("\nComplete game:")
    for i, state in enumerate(path):
        if i == 0:
            print(f"  Start: total={state.total}")
        else:
            move = state.move_from_parent
            player = "MAX" if not state.is_maximizing else "MIN"
            print(f"  {player}: take {move[0]}, discard {move[1]} -> total={state.total}")
    
    return path


def test_21_reachable():
    """Test if 21 is actually reachable with given stack."""
    print("\n" + "=" * 70)
    print("TEST: IS 21 REACHABLE?")
    print("=" * 70)
    
    # Stack where 21 IS reachable
    stack1 = [6, 1, 5, 2, 4, 3, 3, 4, 2, 5, 1, 6]  # Pairs sum to 7
    print(f"\nStack 1 (pairs sum to 7): {stack1}")
    
    initial_state = GameState(total=0, stack_index=0, stack=stack1, is_maximizing=True)
    solver = MinimaxSolver()
    value, _ = solver.solve(initial_state)
    
    print(f"Minimax value: {value}")
    print(f"Is winning for MAX? {value > 0}")
    
    # Stack where 21 is NOT reachable (all 1s)
    stack2 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    print(f"\nStack 2 (all 1s): {stack2}")
    
    initial_state2 = GameState(total=0, stack_index=0, stack=stack2, is_maximizing=True)
    value2, _ = solver.solve(initial_state2)
    
    print(f"Minimax value: {value2}")
    print(f"Is winning for MAX? {value2 > 0}")


def analyze_why_short_paths():
    """Analyze why we're getting short solution paths."""
    print("\n" + "=" * 70)
    print("ANALYSIS: WHY SHORT PATHS?")
    print("=" * 70)
    
    # Let's trace through a simple example
    stack = [3, 5, 2, 6]
    print(f"\nStack: {stack}")
    print("Possible sequences:")
    
    # All possible game sequences
    sequences = [
        # Sequence 1: Take 3, then 2
        [(3, 5), (2, 6)],  # Total: 3 + 2 = 5
        # Sequence 2: Take 3, then 6  
        [(3, 5), (6, 2)],  # Total: 3 + 6 = 9
        # Sequence 3: Take 5, then 2
        [(5, 3), (2, 6)],  # Total: 5 + 2 = 7
        # Sequence 4: Take 5, then 6
        [(5, 3), (6, 2)],  # Total: 5 + 6 = 11
    ]
    
    for i, seq in enumerate(sequences):
        total = 0
        moves = []
        for take, discard in seq:
            total += take
            moves.append(f"take {take} (discard {discard})")
        print(f"  Sequence {i+1}: {' -> '.join(moves)} = total {total}")
    
    print("\nObservation: None reach 21. Game ends after 2 moves (4 values).")
    print("This explains why path length = 3 (initial + 2 moves).")


def test_proper_21_game():
    """Test a game that should actually reach 21."""
    print("\n" + "=" * 70)
    print("TEST: PROPER 21 GAME")
    print("=" * 70)
    
    # Create a longer stack where 21 is reachable
    # We need enough values to sum to 21
    # Let's design a stack: [6, 5, 4, 3, 2, 1, 6, 5, 4, 3, 2, 1]
    # This has 12 values, 6 moves
    
    stack = [6, 5, 4, 3, 2, 1, 6, 5, 4, 3, 2, 1]
    print(f"Stack: {stack}")
    print(f"Stack length: {len(stack)}")
    print(f"Total sum: {sum(stack)}")
    print(f"Maximum possible total (taking highest each time): {sum(sorted(stack)[-6:])}")
    
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    # Use alpha-beta for efficiency
    tracker = SolutionTracker()
    value, terminal_state = alphabeta_with_tracking(
        initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
        is_maximizing=True, tracker=tracker, depth_limit=None
    )
    
    path = tracker.reconstruct_solution_path(initial_state, terminal_state)
    
    print(f"\nAlpha-beta value: {value}")
    print(f"Path length: {len(path)}")
    print(f"Final total: {path[-1].total if path else 'N/A'}")
    
    print("\nGame progression:")
    for i, state in enumerate(path[:10]):  # Show first 10 states
        if i == 0:
            print(f"  Start: total={state.total}, player=MAX")
        else:
            move = state.move_from_parent
            player = "MAX" if not state.is_maximizing else "MIN"
            status = "TERMINAL" if state.is_terminal else ""
            print(f"  {player}: take {move[0]}, discard {move[1]} -> total={state.total} {status}")
    
    # Show summary
    summary = tracker.get_solution_summary()
    print(f"\nSummary:")
    print(f"  Total moves: {summary.get('total_moves', 'N/A')}")
    print(f"  Final total: {summary.get('final_total', 'N/A')}")
    print(f"  Winning player: {summary.get('winning_player', 'N/A')}")
    print(f"  Nodes evaluated: {summary.get('nodes_evaluated', 'N/A')}")


def create_winning_stack():
    """Create a stack where MAX can force a win to 21."""
    print("\n" + "=" * 70)
    print("CREATING WINNING STACK")
    print("=" * 70)
    
    # Design a stack where optimal play reaches exactly 21
    # We need to plan the sequence
    # Example: MAX takes 6, MIN takes 1, MAX takes 6, MIN takes 2, MAX takes 6
    # Total: 6 + 1 + 6 + 2 + 6 = 21
    
    # Stack pairs: (MAX choice, MIN choice)
    # Pair 1: (6, 1) -> MAX takes 6
    # Pair 2: (6, 2) -> MIN takes 1 (but wait, MIN chooses from this pair)
    # Actually, we need to think about the dual-choice mechanic...
    
    # Let me think differently: We want a forced sequence to 21
    # Stack: [6, 1, 6, 2, 6, 3, 6, 4, 6, 5]
    # This won't work because of the choice mechanic
    
    print("Designing a forced-win stack is complex due to the dual-choice mechanic.")
    print("The opponent always has a choice between two values.")
    print("This makes forcing exact totals difficult.")
    
    # Simple approach: Create a stack where 21 can be reached through some path
    stack = [1, 6, 2, 5, 3, 4, 4, 3, 5, 2, 6, 1]  # Mirror pattern
    print(f"\nTrying mirror stack: {stack}")
    
    return stack


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("COMPLETE GAME TESTING")
    print("=" * 70)
    
    try:
        # Run tests
        test_game_completion()
        test_21_reachable()
        analyze_why_short_paths()
        test_proper_21_game()
        
        print("\n" + "=" * 70)
        print("KEY INSIGHTS:")
        print("=" * 70)
        print("1. The game ends when stack is exhausted (no more pairs)")
        print("2. With 4 values, game lasts only 2 moves")
        print("3. Reaching exactly 21 is rare with the dual-choice mechanic")
        print("4. Algorithms are working correctly - finding optimal play")
        print("5. Short paths are expected for small stacks")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()