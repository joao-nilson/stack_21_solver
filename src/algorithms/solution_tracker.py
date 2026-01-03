from typing import List, Dict, Any, Optional
from src.game.game_state import GameState


class SolutionTracker:
    
    def __init__(self):
        self.best_path = []           # Complete optimal path
        self.decision_points = []     # Critical decision points
        self.pruned_branches = 0      # Count of pruned branches
        self.nodes_evaluated = 0      # Count of evaluated nodes
    
    def record_best_move(self, state: GameState, best_child: Optional[GameState], 
                        depth: int, alpha: float, beta: float) -> None:
        decision = {
            'depth': depth,
            'total': state.total,
            'stack_index': state.stack_index,
            'is_maximizing': state.is_maximizing,
            'move': state.move_from_parent if state.move_from_parent else None,
            'best_move': best_child.move_from_parent if best_child else None,
            'value': best_child.value if best_child else state.value,
            'alpha': alpha,
            'beta': beta,
            'children_count': len(state.get_possible_moves())
        }
        self.decision_points.append(decision)
    
    def reconstruct_solution_path(self, root_state: GameState, 
                                terminal_state: Optional[GameState]) -> List[GameState]:
        if terminal_state is None:
            return []
        
        # Reconstruct path from terminal to root
        path = []
        current = terminal_state
        
        while current is not None:
            path.append(current)
            current = current.parent
        
        # Reverse to get from root to terminal
        self.best_path = list(reversed(path))
        return self.best_path
    
    def get_solution_summary(self) -> Dict[str, Any]:
        if not self.best_path:
            return {}
            
        terminal_state = self.best_path[-1] if self.best_path else None
        
        summary = {
            'total_moves': len(self.best_path) - 1,  # Exclude root
            'final_total': terminal_state.total if terminal_state else 0,
            'nodes_evaluated': self.nodes_evaluated,
            'pruned_branches': self.pruned_branches,
            'pruning_efficiency': self.pruned_branches / (self.nodes_evaluated + self.pruned_branches) 
                                  if (self.nodes_evaluated + self.pruned_branches) > 0 else 0,
            'decision_points': len(self.decision_points)
        }
        
        # Add move-by-move sequence (without GameState objects)
        summary['move_sequence'] = []
        for i in range(1, len(self.best_path)):
            state = self.best_path[i]
            if state.move_from_parent:
                move_info = {
                    'player': 'MAX' if not state.is_maximizing else 'MIN',  # Player who made the move
                    'turn': i,
                    'value_taken': state.move_from_parent[0],
                    'value_discarded': state.move_from_parent[1],
                    'new_total': state.total,
                    'is_terminal': state.is_terminal,
                    'evaluation': state.value
                }
                summary['move_sequence'].append(move_info)
        
        # Determine winner
        if terminal_state:
            if terminal_state.total == 21:
                # Player who made the last move wins
                summary['winning_player'] = 'MAX' if not terminal_state.is_maximizing else 'MIN'
                summary['win_reason'] = 'reached_21'
            elif terminal_state.total > 21:
                # Player who made the last move loses
                summary['winning_player'] = 'MIN' if not terminal_state.is_maximizing else 'MAX'
                summary['win_reason'] = 'opponent_busted'
            else:
                summary['winning_player'] = 'None'
                summary['win_reason'] = 'stack_exhausted'
        
        return summary