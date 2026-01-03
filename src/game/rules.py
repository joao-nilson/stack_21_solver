from typing import List, Tuple, Optional, Dict, Any
from enum import Enum


class GamePhase(Enum):
    INITIAL = "initial"
    IN_PROGRESS = "in_progress"
    TERMINAL = "terminal"
    DRAW = "draw"


class Player(Enum):
    MAX = "MAX"  # AI player (maximizing)
    MIN = "MIN"  # Opponent player (minimizing)


class GameRules:    
    WINNING_SCORE = 21
    MIN_VALUE = 1
    MAX_VALUE = 6
    
    @staticmethod
    def is_valid_move(current_total: int, move_value: int) -> bool:
        if not (GameRules.MIN_VALUE <= move_value <= GameRules.MAX_VALUE):
            return False
        
        return True
    
    @staticmethod
    def get_available_moves(current_total: int, stack_segment: List[int]) -> List[Dict[str, Any]]:
        if len(stack_segment) < 2:
            return []
        
        val1, val2 = stack_segment[0], stack_segment[1]
        
        moves = [
            {
                "value_taken": val1,
                "value_discarded": val2,
                "new_total": current_total + val1,
                "description": f"Take {val1} (discard {val2}) -> Total: {current_total + val1}"
            },
            {
                "value_taken": val2,
                "value_discarded": val1,
                "new_total": current_total + val2,
                "description": f"Take {val2} (discard {val1}) -> Total: {current_total + val2}"
            }
        ]
        
        return moves
    
    @staticmethod
    def check_terminal_state(total: int, stack_index: int, stack_length: int) -> Tuple[bool, Optional[Dict]]:
        terminal_info = None
        
        # Game ends if exactly 21 is reached
        if total == GameRules.WINNING_SCORE:
            terminal_info = {
                "reason": "reached_21",
                "winner": "player_who_made_move",
                "score": total
            }
            return True, terminal_info
        
        # Game ends if total exceeds 21 (player who made move loses)
        if total > GameRules.WINNING_SCORE:
            terminal_info = {
                "reason": "exceeded_21",
                "loser": "player_who_made_move",
                "score": total
            }
            return True, terminal_info
        
        # Game ends if stack is exhausted
        if stack_index >= stack_length - 1: 
            terminal_info = {
                "reason": "stack_exhausted",
                "score": total,
                "closest_to_21": True  
            }
            return True, terminal_info
        
        return False, terminal_info
    
    @staticmethod
    def evaluate_position(total: int, player: Player, stack_remaining: List[int]) -> float:
        if total == GameRules.WINNING_SCORE:
            return 1000 if player == Player.MAX else -1000
        
        if total > GameRules.WINNING_SCORE:
            return -1000 if player == Player.MAX else 1000
        
        base_score = GameRules.WINNING_SCORE - total
        
        if player == Player.MAX:
            score = base_score
        else:
            score = -base_score
        
        if stack_remaining:
            avg_remaining = sum(stack_remaining) / len(stack_remaining)
            stack_factor = avg_remaining / GameRules.MAX_VALUE
            
            if player == Player.MAX:
                score *= (1 + stack_factor * 0.1)
            else:
                score *= (1 - stack_factor * 0.1)
        
        return score
    
    @staticmethod
    def determine_winner(final_total: int, last_player: Player) -> Tuple[Optional[Player], str]:
        if final_total == GameRules.WINNING_SCORE:
            winner = last_player
            return winner, f"Reached exactly {GameRules.WINNING_SCORE}"
        
        if final_total > GameRules.WINNING_SCORE:
            winner = Player.MIN if last_player == Player.MAX else Player.MAX
            return winner, f"Opponent exceeded {GameRules.WINNING_SCORE}"
        
        return None, "Game ended with stack exhaustion"
    
    @staticmethod
    def calculate_forced_wins(stack: List[int]) -> Dict[str, Any]:
        analysis = {
            "winning_positions": [],  # Positions where player to move can force win
            "losing_positions": [],   # Positions where all moves lead to loss
            "safe_totals": []         # Totals that are safe (can't lose immediately)
        }
        
        # Simple analysis: positions where you can reach 21 in one move
        for total in range(1, GameRules.WINNING_SCORE + 1):
            for move in range(GameRules.MIN_VALUE, GameRules.MAX_VALUE + 1):
                if total + move == GameRules.WINNING_SCORE:
                    analysis["winning_positions"].append({
                        "total": total,
                        "winning_move": move
                    })
                    break
        
        # Safe totals: totals where opponent can't reach 21 in one move
        for total in range(1, GameRules.WINNING_SCORE + 1):
            safe = True
            for opponent_move in range(GameRules.MIN_VALUE, GameRules.MAX_VALUE + 1):
                if total + opponent_move == GameRules.WINNING_SCORE:
                    safe = False
                    break
            if safe:
                analysis["safe_totals"].append(total)
        
        return analysis
    
    @staticmethod
    def validate_game_state(total: int, stack_index: int, stack: List[int]) -> Tuple[bool, str]:
        if total < 0:
            return False, f"Invalid total: {total}"
        
        if stack_index < 0:
            return False, f"Invalid stack index: {stack_index}"
        
        if stack_index >= len(stack):
            return False, f"Stack index {stack_index} out of bounds for stack of length {len(stack)}"
        
        for i, val in enumerate(stack):
            if not (GameRules.MIN_VALUE <= val <= GameRules.MAX_VALUE):
                return False, f"Invalid value {val} at position {i} in stack"
        
        return True, "Valid game state"


# Example usage
if __name__ == "__main__":
    rules = GameRules()
    
    moves = rules.get_available_moves(14, [3, 5])
    print("Available moves from total=14 with [3,5]:")
    for move in moves:
        print(f"  {move['description']}")
    
    terminal, info = rules.check_terminal_state(21, 0, 10)
    print(f"\nTotal=21 is terminal: {terminal}, Info: {info}")
    
    score = rules.evaluate_position(18, Player.MAX, [1, 2, 3])
    print(f"\nEvaluation for MAX at 18 with [1,2,3] remaining: {score}")