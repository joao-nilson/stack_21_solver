class GameState:    
    def __init__(self, total=0, stack_index=0, stack=None, is_maximizing=True, parent=None, move_from_parent=None):
        self.total = total
        self.stack_index = stack_index
        self.stack = stack or [] 
        self.is_maximizing = is_maximizing
        self.parent = parent
        self.move_from_parent = move_from_parent
        self.value = None
        self.children = []
        self.is_terminal = self._check_terminal()
    
    def _check_terminal(self):
        if self.total == 21:
            return True
        if self.total > 21:
            return True
        if self.stack_index >= len(self.stack) - 1:
            return True
        return False
    
    def evaluate(self):
        if self.total == 21:
            return 1000 if self.is_maximizing else -1000
        if self.total > 21:
            return -1000 if self.is_maximizing else 1000
        
        # Game ended due to stack exhaustion
        if self.is_terminal and self.stack_index >= len(self.stack) - 1:
            # Closer to 21 is better for MAX, worse for MIN
            score = 21 - self.total  # Positive if total < 21, negative if total > 21
            return score if self.is_maximizing else -score
        
        # Non-terminal state: heuristic based on remaining possibilities
        # Base heuristic: closeness to 21 without going over
        if self.total > 21:
            # Already over, but not marked terminal? Shouldn't happen
            return -500 if self.is_maximizing else 500
        
        # Calculate remaining values in stack
        remaining_values = self.stack[self.stack_index:] if self.stack_index < len(self.stack) else []
        
        # Simple heuristic: how close to 21, adjusted by remaining values
        base_score = 21 - self.total
        
        # Adjust based on remaining values (more high values is better for reaching 21)
        if remaining_values:
            avg_remaining = sum(remaining_values) / len(remaining_values)
            # Having higher average remaining values is better
            adjustment = (avg_remaining - 3.5) / 10  # 3.5 is average of 1-6
            base_score *= (1 + adjustment)
        
        return base_score if self.is_maximizing else -base_score
    
    def get_possible_moves(self):
        if self.is_terminal:
            return []
        
        val1 = self.stack[self.stack_index]
        val2 = self.stack[self.stack_index + 1]
        
        moves = [
            (val1, val2, self.total + val1),
            (val2, val1, self.total + val2)
        ]
        
        return moves
    
    def apply_move(self, move):
        value_taken, value_discarded, new_total = move
        
        return GameState(
            total=new_total,
            stack_index=self.stack_index + 2,
            stack=self.stack,
            is_maximizing=not self.is_maximizing,
            parent=self,
            move_from_parent=move
        )
    
    def get_path_from_root(self):
        path = []
        current = self
        while current:
            path.append(current)
            current = current.parent
        return list(reversed(path))