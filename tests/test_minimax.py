import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.game.game_state import GameState
from src.algorithms.minimax import MinimaxSolver


class TestMinimax:    
    def test_minimax_simple_win(self):
        # Stack: [6, 6, 3, 2] - Starting with 6 leads to 21
        stack = [6, 6, 3, 2]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        solver = MinimaxSolver()
        value, best_child = solver.solve(initial_state)
        
        # Should find a winning move
        assert value > 0
        assert best_child is not None
        
        # The winning move should be to take 6
        if best_child.move_from_parent:
            assert best_child.move_from_parent[0] == 6
    
    def test_minimax_forced_loss(self):
        # Stack: [6, 6, 6, 6] - All 6s, will bust
        stack = [6, 6, 6, 6]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        solver = MinimaxSolver()
        value, best_child = solver.solve(initial_state)
        
        # Should find a losing position
        assert value < 0
    
    def test_minimax_depth_limit(self):
        stack = [1, 2, 3, 4, 5, 6, 1, 2, 3, 4]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        solver = MinimaxSolver(depth_limit=2)
        value, best_child = solver.solve(initial_state)
        
        # Should complete within depth limit
        stats = solver.get_statistics()
        assert stats['max_depth_reached'] <= 2
    
    def test_minimax_statistics(self):
        stack = [1, 2, 3, 4]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        solver = MinimaxSolver()
        solver.solve(initial_state)
        
        stats = solver.get_statistics()
        
        assert stats['nodes_evaluated'] > 0
        assert stats['execution_time_seconds'] > 0
        assert stats['algorithm'] == 'minimax'
    
    def test_minimax_move_analysis(self):
        stack = [3, 5, 2, 6]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        solver = MinimaxSolver()
        moves_analysis = solver.analyze_move_quality(initial_state)
        
        assert len(moves_analysis) == 2  # Should have 2 possible moves
        assert all('evaluation' in move for move in moves_analysis)
        assert all('interpretation' in move for move in moves_analysis)
    
    def test_minimax_path_reconstruction(self):
        stack = [1, 2, 3, 4]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        solver = MinimaxSolver()
        path = solver.find_optimal_path(initial_state)
        
        assert len(path) > 1
        assert path[0].total == 0
        assert path[-1].is_terminal
    
    def test_minimax_memoization(self):
        stack = [1, 2, 3, 4, 5, 6, 1, 2]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        
        solver1 = MinimaxSolver()
        solver1.solve(initial_state)
        nodes1 = solver1.get_statistics()['nodes_evaluated']
        
        # Create a state that should hit the transposition table
        # This is tricky because we need identical states reachable by different paths
        # For now, just verify memoization doesn't break anything
        assert nodes1 > 0
    
    def test_minimax_consistency(self):
        stack = [1, 2, 3, 4]
        state1 = GameState(total=10, stack_index=2, stack=stack, is_maximizing=True)
        state2 = GameState(total=10, stack_index=2, stack=stack, is_maximizing=True)
        
        solver = MinimaxSolver()
        value1, _ = solver.solve(state1)
        solver.reset()
        value2, _ = solver.solve(state2)
        
        # Values should be the same (within floating point tolerance)
        assert abs(value1 - value2) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])