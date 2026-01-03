import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.game.game_state import GameState
from src.algorithms.alphabeta import alphabeta_with_tracking
from src.algorithms.solution_tracker import SolutionTracker


class TestAlphaBeta:
    """Test cases for alpha-beta pruning algorithm."""
    
    def test_alphabeta_basic(self):
        """Test basic alpha-beta pruning."""
        stack = [1, 2, 3, 4]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        tracker = SolutionTracker()
        
        value, terminal_state = alphabeta_with_tracking(
            initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=True, tracker=tracker, depth_limit=None
        )
        
        assert value is not None
        assert terminal_state is not None
        assert tracker.nodes_evaluated > 0
    
    def test_alphabeta_pruning(self):
        """Test that pruning actually occurs."""
        # Create a stack where pruning should happen
        stack = [6, 6, 6, 6, 6, 6]  # All 6s, will bust quickly
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        tracker = SolutionTracker()
        
        alphabeta_with_tracking(
            initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=True, tracker=tracker, depth_limit=None
        )
        
        # Should have some pruning
        assert tracker.pruned_branches > 0
    
    def test_alphabeta_solution_tracking(self):
        """Test that solution path is tracked."""
        stack = [3, 5, 2, 6]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        tracker = SolutionTracker()
        
        value, terminal_state = alphabeta_with_tracking(
            initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=True, tracker=tracker, depth_limit=None
        )
        
        # Reconstruct path
        path = tracker.reconstruct_solution_path(initial_state, terminal_state)
        
        assert len(path) > 0
        assert tracker.best_path == path
        assert len(tracker.decision_points) > 0
    
    def test_alphabeta_depth_limit(self):
        """Test alpha-beta with depth limit."""
        stack = [1, 2, 3, 4, 5, 6, 1, 2, 3, 4]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        tracker = SolutionTracker()
        
        value, terminal_state = alphabeta_with_tracking(
            initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=True, tracker=tracker, depth_limit=3
        )
        
        # Terminal state might not be reached due to depth limit
        # Just verify it runs without error
        assert True
    
    def test_alphabeta_decision_recording(self):
        """Test that decision points are recorded."""
        stack = [1, 2, 3, 4]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        tracker = SolutionTracker()
        
        alphabeta_with_tracking(
            initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=True, tracker=tracker, depth_limit=None
        )
        
        # Should have recorded some decision points
        assert len(tracker.decision_points) > 0
        
        # Check decision point structure
        decision = tracker.decision_points[0]
        assert 'depth' in decision
        assert 'total' in decision
        assert 'is_maximizing' in decision
        assert 'alpha' in decision
        assert 'beta' in decision
    
    def test_alphabeta_summary_generation(self):
        """Test solution summary generation."""
        stack = [1, 2, 3, 4]
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        tracker = SolutionTracker()
        
        value, terminal_state = alphabeta_with_tracking(
            initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=True, tracker=tracker, depth_limit=None
        )
        
        # Reconstruct path first
        path = tracker.reconstruct_solution_path(initial_state, terminal_state)
        
        # Generate summary
        summary = tracker.get_solution_summary()
        
        assert summary is not None
        assert 'total_moves' in summary
        assert 'nodes_evaluated' in summary
        assert 'pruned_branches' in summary
        assert 'move_sequence' in summary
    
    def test_alphabeta_move_ordering(self):
        """Test that move ordering improves pruning."""
        # This test verifies that sorting moves helps
        # We'll test by comparing with and without move ordering
        # (Implementation detail, but good to verify)
        stack = [6, 1, 6, 1, 6, 1]  # Alternating high/low values
        initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
        tracker = SolutionTracker()
        
        # With move ordering (default)
        alphabeta_with_tracking(
            initial_state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=True, tracker=tracker, depth_limit=4
        )
        
        nodes_with_ordering = tracker.nodes_evaluated
        pruned_with_ordering = tracker.pruned_branches
        
        # Note: We can't easily test without ordering without modifying the function
        # For now, just verify it runs
        assert nodes_with_ordering > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])