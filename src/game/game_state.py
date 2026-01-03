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
        if self.total > 21:
            return -10000 if self.is_maximizing else 10000
        
        if self.total == 21:
            return 10000 if self.is_maximizing else -10000
        
        if self.is_terminal:
            return self.total if self.is_maximizing else -self.total
        
        remaining_values = self.stack[self.stack_index:] if self.stack_index < len(self.stack) else []
        remaining_pairs = len(remaining_values) // 2
        
        sorted_remaining = sorted(remaining_values)
        
        max_best_total = self.total
        max_worst_total = self.total
        
        temp_values = sorted_remaining.copy()
        
        for i in range(remaining_pairs):
            max_best_total += temp_values.pop() if temp_values else 0
        
        score = self.total * 10
        
        # Bonus for being close to 21
        if 15 <= self.total <= 20:
            score += (self.total - 14) * 100
        
        # Penalty for being too low
        if self.total < 10:
            score -= (10 - self.total) * 50
        
        # Consider remaining stack - more options is generally good
        score += len(remaining_values) * 5
        
        return score if self.is_maximizing else -score
    
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