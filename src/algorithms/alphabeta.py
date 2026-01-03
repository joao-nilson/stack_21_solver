import time
from typing import Tuple, Optional, Dict, Any
from src.game.game_state import GameState
from src.algorithms.solution_tracker import SolutionTracker


def alphabeta_with_tracking(state: GameState, depth: int, alpha: float, beta: float, 
                           is_maximizing: bool, tracker: SolutionTracker, 
                           depth_limit: Optional[int] = None) -> Tuple[float, Optional[GameState]]:

    tracker.nodes_evaluated += 1
    
    # Check terminal or depth limit
    if state.is_terminal or (depth_limit and depth >= depth_limit):
        state.value = state.evaluate()
        return state.value, state
    
    if is_maximizing:
        best_value = float('-inf')
        best_child = None
        
        # Get moves and sort for better pruning (highest value first for MAX)
        moves = state.get_possible_moves()
        moves.sort(key=lambda x: x[2], reverse=True)  # Sort by new_total descending
        
        for i, move in enumerate(moves):
            child_state = state.apply_move(move)
            
            value, terminal_state = alphabeta_with_tracking(
                child_state, depth + 1, alpha, beta, False, tracker, depth_limit
            )
            child_state.value = value
            
            if value > best_value:
                best_value = value
                best_child = child_state
                best_terminal = terminal_state
            
            alpha = max(alpha, best_value)
            
            # Beta cutoff - prune remaining branches
            if alpha >= beta:
                tracker.pruned_branches += len(moves) - i - 1
                tracker.record_best_move(state, best_child, depth, alpha, beta)
                return best_value, best_terminal
        
        state.value = best_value
        tracker.record_best_move(state, best_child, depth, alpha, beta)
        return best_value, best_terminal if best_child else state
        
    else:  # Minimizing player
        best_value = float('inf')
        best_child = None
        
        moves = state.get_possible_moves()
        moves.sort(key=lambda x: x[2])  # Sort by new_total ascending for MIN
        
        for i, move in enumerate(moves):
            child_state = state.apply_move(move)
            
            value, terminal_state = alphabeta_with_tracking(
                child_state, depth + 1, alpha, beta, True, tracker, depth_limit
            )
            child_state.value = value
            
            if value < best_value:
                best_value = value
                best_child = child_state
                best_terminal = terminal_state
            
            beta = min(beta, best_value)
            
            # Alpha cutoff - prune remaining branches
            if beta <= alpha:
                tracker.pruned_branches += len(moves) - i - 1
                tracker.record_best_move(state, best_child, depth, alpha, beta)
                return best_value, best_terminal
        
        state.value = best_value
        tracker.record_best_move(state, best_child, depth, alpha, beta)
        return best_value, best_terminal if best_child else state


# Alternative: Class-based implementation
class AlphaBetaSolver:
    
    def __init__(self, depth_limit: Optional[int] = None):
        self.depth_limit = depth_limit
        self.tracker = SolutionTracker()
        
    def solve(self, state: GameState) -> Tuple[float, GameState]:
        value, terminal_state = alphabeta_with_tracking(
            state, depth=0, alpha=float('-inf'), beta=float('inf'),
            is_maximizing=state.is_maximizing, tracker=self.tracker,
            depth_limit=self.depth_limit
        )
        return value, terminal_state
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "algorithm": "alpha-beta",
            "nodes_evaluated": self.tracker.nodes_evaluated,
            "pruned_branches": self.tracker.pruned_branches,
            "decision_points": len(self.tracker.decision_points),
            "pruning_efficiency": self.tracker.pruned_branches / 
                                 (self.tracker.nodes_evaluated + self.tracker.pruned_branches)
                                 if (self.tracker.nodes_evaluated + self.tracker.pruned_branches) > 0 else 0
        }
    
    def get_solution_path(self, initial_state: GameState) -> list:
        value, terminal_state = self.solve(initial_state)
        return self.tracker.reconstruct_solution_path(initial_state, terminal_state)