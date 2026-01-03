import json
from typing import List, Dict, Any, Optional
from src.game.game_state import GameState
from src.game.rules import Player


class PathVisualizer:    
    def __init__(self, show_colors: bool = True):
        self.show_colors = show_colors
        self.colors = {
            'MAX': '\033[94m',      # Blue
            'MIN': '\033[91m',      # Red  
            'WIN': '\033[92m',      # Green
            'LOSE': '\033[91m',     # Red
            'MOVE': '\033[93m',     # Yellow
            'TOTAL': '\033[96m',    # Cyan
            'RESET': '\033[0m'      # Reset
        }
    
    def visualize_solution_path(self, path: List[GameState], show_details: bool = True) -> str:

        if not path:
            return "No solution path available."
        
        output = []
        output.append(self._create_header("OPTIMAL SOLUTION PATH"))
        output.append("")
        
        initial_state = path[0]
        terminal_state = path[-1]
        
        output.append(self._create_summary(initial_state, terminal_state, len(path)))
        output.append("")
        
        output.append(self._create_move_sequence(path))
        output.append("")
        
        if show_details:
            output.append(self._create_decision_analysis(path))
            output.append("")
            
            output.append(self._create_alternative_analysis(path))
            output.append("")
        
        return "\n".join(output)
    
    def _create_header(self, title: str) -> str:
        """Create formatted header."""
        border = "=" * 70
        padding = (70 - len(title) - 2) // 2
        title_line = f"{' ' * padding} {title} {' ' * padding}"
        if self.show_colors:
            return f"\n{self.colors['MOVE']}{border}\n{title_line}\n{border}{self.colors['RESET']}"
        else:
            return f"\n{border}\n{title_line}\n{border}"
    
    def _create_summary(self, initial: GameState, terminal: GameState, path_length: int) -> str:
        """Create game summary."""
        summary_lines = []
        summary_lines.append("GAME SUMMARY:")
        summary_lines.append(f"  Stack: {initial.stack}")
        summary_lines.append(f"  Stack length: {len(initial.stack)}")
        summary_lines.append(f"  Total moves in solution: {path_length - 1}")
        summary_lines.append(f"  Final total: {terminal.total}")
        
        # Determine winner
        if terminal.total == 21:
            # Player who made the last move wins
            winner = "MIN" if terminal.is_maximizing else "MAX"  # Terminal state has next player's turn
            summary_lines.append(f"  Winner: {self._colorize(winner, winner)} (reached 21 exactly)")
        elif terminal.total > 21:
            # Player who made the last move loses
            loser = "MIN" if terminal.is_maximizing else "MAX"
            winner = "MAX" if loser == "MIN" else "MIN"
            summary_lines.append(f"  Winner: {self._colorize(winner, winner)} (opponent bust)")
        else:
            summary_lines.append(f"  Result: Game ended with total {terminal.total}")
        
        if terminal.value is not None:
            summary_lines.append(f"  Minimax value: {terminal.value:.1f}")
        
        return "\n".join(summary_lines)
    
    def _create_move_sequence(self, path: List[GameState]) -> str:
        sequence_lines = ["MOVE SEQUENCE:"]
        
        for i, state in enumerate(path):
            if i == 0:
                sequence_lines.append(f"\nTurn 0: Initial State")
                sequence_lines.append(f"  Total: {state.total}")
                sequence_lines.append(f"  Player to move: {self._colorize_player(state.is_maximizing)}")
                sequence_lines.append(f"  Remaining stack: {state.stack}")
                continue
            
            move = state.move_from_parent
            if not move:
                continue
            
            value_taken, value_discarded, new_total = move
            
            player_moved = "MAX" if not state.is_maximizing else "MIN"
            
            sequence_lines.append(f"\nTurn {i}: {self._colorize_player(player_moved == 'MAX')}")
            sequence_lines.append(f"  Action: Take {self._colorize(value_taken, 'MOVE')}, "
                                f"Discard {value_discarded}")
            sequence_lines.append(f"  New total: {self._colorize(new_total, 'TOTAL')}")
            
            if state.stack_index < len(state.stack):
                remaining = state.stack[state.stack_index:]
                sequence_lines.append(f"  Remaining stack: {remaining}")
            
            # Show evaluation if available
            if state.value is not None:
                eval_text = self._interpret_evaluation(state.value, state.is_maximizing)
                sequence_lines.append(f"  Position evaluation: {state.value:.1f} ({eval_text})")
            
            # Highlight if this leads to terminal state
            if state.is_terminal:
                if state.total == 21:
                    sequence_lines.append(f"  {self._colorize('→ WINNING MOVE!', 'WIN')}")
                elif state.total > 21:
                    sequence_lines.append(f"  {self._colorize('→ BUST! Opponent wins.', 'LOSE')}")
        
        return "\n".join(sequence_lines)
    
    def _create_decision_analysis(self, path: List[GameState]) -> str:
        analysis_lines = ["CRITICAL DECISION ANALYSIS:"]
        
        critical_turns = []
        
        for i, state in enumerate(path):
            if i == 0 or i == len(path) - 1:
                continue
            
            if self._is_critical_decision(state, path[i-1]):
                move = state.move_from_parent
                player = "MAX" if not state.is_maximizing else "MIN"  # Player who made the move
                
                # Find alternative moves
                parent = path[i-1]
                alternatives = []
                for alt_move in parent.get_possible_moves():
                    if alt_move != move:
                        alternatives.append(alt_move)
                
                analysis_lines.append(f"\n  Turn {i}: {player}'s critical decision")
                analysis_lines.append(f"    Chose: Take {move[0]}, discard {move[1]}")
                analysis_lines.append(f"    Alternatives:")
                for alt in alternatives:
                    outcome = self._predict_outcome(alt[2], state.stack_index)
                    analysis_lines.append(f"      - Take {alt[0]}, discard {alt[1]} → Total: {alt[2]} {outcome}")
        
        if len(critical_turns) == 0:
            analysis_lines.append("\n  No critical decisions found (path is forced or trivial)")
        
        return "\n".join(analysis_lines)
    
    def _create_alternative_analysis(self, path: List[GameState]) -> str:
        analysis_lines = ["WHAT-IF SCENARIOS:"]
        
        max_analysis_moves = min(3, len(path) - 1)
        
        for i in range(1, max_analysis_moves + 1):
            state = path[i]
            parent = path[i-1]
            move = state.move_from_parent
            
            analysis_lines.append(f"\n  At turn {i} (total: {parent.total}):")
            analysis_lines.append(f"    Optimal: {self._colorize(f'Take {move[0]}, discard {move[1]}', 'MOVE')}")
            
            for alt_move in parent.get_possible_moves():
                if alt_move != move:
                    diff = abs(alt_move[2] - move[2])
                    analysis_lines.append(f"    Alternative: Take {alt_move[0]}, discard {alt_move[1]} "
                                        f"(diff: {diff:+d})")
        
        return "\n".join(analysis_lines)
    
    def _is_critical_decision(self, state: GameState, parent_state: GameState) -> bool:
        if not parent_state.children:
            return False
        
        values = [child.value for child in parent_state.children if child.value is not None]
        
        if not values:
            return False
        
        # Decision is critical if not all moves lead to same outcome
        unique_values = len(set(round(v, 2) for v in values))
        
        # Also critical if it's a winning/losing move
        if state.value is not None and abs(state.value) >= 100:
            return True
        
        return unique_values > 1
    
    def _predict_outcome(self, total: int, stack_index: int) -> str:
        if total == 21:
            return self._colorize("(Win!)", "WIN")
        elif total > 21:
            return self._colorize("(Lose)", "LOSE")
        else:
            remaining = 21 - total
            return f"(Need {remaining})"
    
    def _colorize(self, text: str, color_type: str) -> str:
        if self.show_colors and color_type in self.colors:
            return f"{self.colors[color_type]}{text}{self.colors['RESET']}"
        return text
    
    def _colorize_player(self, is_maximizing: bool) -> str:
        player = "MAX" if is_maximizing else "MIN"
        return self._colorize(player, player)
    
    def _interpret_evaluation(self, value: float, is_maximizing: bool) -> str:
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
    
    def export_path_json(self, path: List[GameState], filename: str) -> None:
        path_data = {
            "moves": [],
            "statistics": self._get_path_statistics(path)
        }
        
        for i, state in enumerate(path):
            move_data = {
                "turn": i,
                "total": state.total,
                "player_to_move": "MAX" if state.is_maximizing else "MIN",
                "stack_index": state.stack_index,
                "is_terminal": state.is_terminal,
                "value": state.value
            }
            
            if i > 0 and state.move_from_parent:
                move_data["move"] = {
                    "value_taken": state.move_from_parent[0],
                    "value_discarded": state.move_from_parent[1],
                    "new_total": state.move_from_parent[2]
                }
            
            if state.stack_index < len(state.stack):
                move_data["remaining_stack"] = state.stack[state.stack_index:]
            
            path_data["moves"].append(move_data)
        
        with open(filename, 'w') as f:
            json.dump(path_data, f, indent=2, default=str)
        
        print(f"Path exported to {filename}")
    
    def _get_path_statistics(self, path: List[GameState]) -> Dict[str, Any]:
        if not path:
            return {}
        
        terminal = path[-1]
        
        stats = {
            "total_moves": len(path) - 1,
            "final_total": terminal.total,
            "stack_usage": f"{terminal.stack_index}/{len(terminal.stack)} values used",
            "is_winning_path": terminal.total == 21,
            "is_bust_path": terminal.total > 21,
            "max_total_reached": max(state.total for state in path),
            "min_total_reached": min(state.total for state in path),
            "average_move_value": sum(
                state.move_from_parent[0] for state in path[1:] if state.move_from_parent
            ) / (len(path) - 1) if len(path) > 1 else 0
        }
        
        max_moves = sum(1 for state in path[1:] if not state.is_maximizing)  # MAX moved to get to this state
        min_moves = sum(1 for state in path[1:] if state.is_maximizing)      # MIN moved to get to this state
        
        stats["max_moves"] = max_moves
        stats["min_moves"] = min_moves
        
        return stats
    
    def create_comparison_report(self, path1: List[GameState], path2: List[GameState], 
                                label1: str = "Path 1", label2: str = "Path 2") -> str:
        output = []
        output.append(self._create_header("PATH COMPARISON"))
        output.append("")
        
        output.append(f"{label1}: {len(path1) - 1} moves, final total: {path1[-1].total if path1 else 'N/A'}")
        output.append(f"{label2}: {len(path2) - 1} moves, final total: {path2[-1].total if path2 else 'N/A'}")
        output.append("")
        
        divergence_point = None
        for i in range(min(len(path1), len(path2))):
            if i == 0:
                continue 
            
            if path1[i].move_from_parent != path2[i].move_from_parent:
                divergence_point = i
                break
        
        if divergence_point:
            output.append(f"First divergence at turn {divergence_point}:")
            output.append(f"  {label1}: Take {path1[divergence_point].move_from_parent[0]}, "
                         f"discard {path1[divergence_point].move_from_parent[1]}")
            output.append(f"  {label2}: Take {path2[divergence_point].move_from_parent[0]}, "
                         f"discard {path2[divergence_point].move_from_parent[1]}")
        else:
            output.append("Paths are identical up to the shorter path's length")
        
        return "\n".join(output)


# Example usage
if __name__ == "__main__":
    from src.game.stack_manager import StackManager
    from src.algorithms.minimax import MinimaxSolver
    
    stack = [3, 5, 2, 6, 4, 1]
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    solver = MinimaxSolver()
    path = solver.find_optimal_path(initial_state)
    
    visualizer = PathVisualizer(show_colors=True)
    visualization = visualizer.visualize_solution_path(path, show_details=True)
    
    print(visualization)
    
    # Export to JSON
    visualizer.export_path_json(path, "solution_path.json")