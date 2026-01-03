import time
from typing import Tuple, Optional, Dict, Any, List
from src.game.game_state import GameState


class MinimaxSolver:
    
    def __init__(self, depth_limit: Optional[int] = None):

        self.depth_limit = depth_limit
        self.nodes_evaluated = 0
        self.max_depth_reached = 0
        self.execution_time = 0
        self.transposition_table = {}  # Basic memoization
        
    def solve(self, state: GameState) -> Tuple[float, Optional[GameState]]:
        start_time = time.time()
        
        # Reset counters
        self.nodes_evaluated = 0
        self.max_depth_reached = 0
        self.transposition_table.clear()
        
        # Run minimax
        value, best_child = self._minimax(state, depth=0)
        
        self.execution_time = time.time() - start_time
        
        return value, best_child
    
    def _minimax(self, state: GameState, depth: int) -> Tuple[float, Optional[GameState]]:
        self.nodes_evaluated += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        
        # Check for depth limit
        if self.depth_limit and depth >= self.depth_limit:
            state.value = state.evaluate()
            return state.value, state
        
        # Check terminal state
        if state.is_terminal:
            state.value = state.evaluate()
            return state.value, state
        
        # Check transposition table (memoization)
        state_key = self._get_state_key(state)
        if state_key in self.transposition_table:
            cached_value, cached_depth, cached_child = self.transposition_table[state_key]
            if cached_depth >= depth:  # If cached at equal or deeper depth
                return cached_value, cached_child
        
        if state.is_maximizing:
            best_value = float('-inf')
            best_child = None
            
            for move in state.get_possible_moves():
                child_state = state.apply_move(move)
                
                child_value, _ = self._minimax(child_state, depth + 1)
                child_state.value = child_value
                
                if child_value > best_value:
                    best_value = child_value
                    best_child = child_state
            
            state.value = best_value
            
            self.transposition_table[state_key] = (best_value, depth, best_child)
            
            return best_value, best_child
        
        else:  # Minimizing player
            best_value = float('inf')
            best_child = None
            
            for move in state.get_possible_moves():
                child_state = state.apply_move(move)
                
                child_value, _ = self._minimax(child_state, depth + 1)
                child_state.value = child_value
                
                if child_value < best_value:
                    best_value = child_value
                    best_child = child_state
            
            state.value = best_value
            
            self.transposition_table[state_key] = (best_value, depth, best_child)
            
            return best_value, best_child
    
    def _get_state_key(self, state: GameState) -> str:
        # Simple key: total + stack position + is_maximizing
        # For more accuracy, include the remaining stack
        remaining_stack = tuple(state.stack[state.stack_index:]) if state.stack_index < len(state.stack) else ()
        return f"{state.total}_{state.stack_index}_{state.is_maximizing}_{remaining_stack}"
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "algorithm": "minimax",
            "nodes_evaluated": self.nodes_evaluated,
            "max_depth_reached": self.max_depth_reached,
            "execution_time_seconds": self.execution_time,
            "transposition_hits": len([v for v in self.transposition_table.values() if v[1] > 0]),
            "depth_limit": self.depth_limit,
            "nodes_per_second": self.nodes_evaluated / self.execution_time if self.execution_time > 0 else 0
        }
    
    def find_optimal_path(self, initial_state: GameState) -> List[GameState]:

        value, terminal_state = self.solve(initial_state)
        
        if terminal_state is None:
            return []
        
        path = []
        current = terminal_state
        
        while current is not None:
            path.append(current)
            current = current.parent
        
        path.reverse()
        
        return path
    
    def analyze_move_quality(self, state: GameState) -> List[Dict[str, Any]]:
        moves_analysis = []
        
        for move in state.get_possible_moves():
            child_state = state.apply_move(move)
            value, _ = self._minimax(child_state, depth=1)
            
            analysis = {
                "move": move,
                "value_taken": move[0],
                "value_discarded": move[1],
                "new_total": move[2],
                "evaluation": value,
                "interpretation": self._interpret_value(value, state.is_maximizing),
                "child_state": child_state
            }
            
            moves_analysis.append(analysis)
        
        if state.is_maximizing:
            moves_analysis.sort(key=lambda x: x["evaluation"], reverse=True)
        else:
            moves_analysis.sort(key=lambda x: x["evaluation"])
        
        return moves_analysis
    
    def _interpret_value(self, value: float, is_maximizing: bool) -> str:
        if abs(value) >= 1000:
            if (value > 0 and is_maximizing) or (value < 0 and not is_maximizing):
                return "Forced win"
            else:
                return "Forced loss"
        elif value > 50:
            return "Strong advantage"
        elif value > 10:
            return "Advantage"
        elif value > -10:
            return "Neutral"
        elif value > -50:
            return "Disadvantage"
        else:
            return "Strong disadvantage"