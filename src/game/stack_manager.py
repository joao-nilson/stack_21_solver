import random
import json
from typing import List, Optional, Tuple
from pathlib import Path


class StackManager:
    @staticmethod
    def generate_random_stack(length: int = 10, min_val: int = 1, max_val: int = 6) -> List[int]:
        if length < 2:
            raise ValueError("Stack length must be at least 2 for dual-value choices")
        
        return [random.randint(min_val, max_val) for _ in range(length)]
    
    @staticmethod
    def generate_balanced_stack(length: int = 12) -> List[int]:
        # Ensure each value 1-6 appears roughly the same number of times
        base_values = list(range(1, 7))
        repetitions = (length // 6) + 1
        
        stack = []
        for _ in range(repetitions):
            random.shuffle(base_values)
            stack.extend(base_values)
        
        # Trim to desired length
        return stack[:length]
    
    @staticmethod
    def generate_biased_stack(length: int = 10, bias_value: int = 6, bias_factor: float = 0.5) -> List[int]:
        if not 1 <= bias_value <= 6:
            raise ValueError("bias_value must be between 1 and 6")
        
        stack = []
        for _ in range(length):
            if random.random() < bias_factor:
                stack.append(bias_value)
            else:
                stack.append(random.randint(1, 6))
        
        return stack
    
    @staticmethod
    def save_stack(stack: List[int], filename: str) -> None:
        data = {
            "stack": stack,
            "length": len(stack),
            "sum": sum(stack),
            "average": sum(stack) / len(stack)
        }
        
        filepath = Path("data") / filename
        filepath.parent.mkdir(exist_ok=True, parents=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Stack saved to {filepath}")
    
    @staticmethod
    def load_stack(filename: str) -> Tuple[List[int], dict]:
        filepath = Path("data") / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Stack file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return data["stack"], data
    
    @staticmethod
    def analyze_stack(stack: List[int]) -> dict:
        if not stack:
            return {}
        
        return {
            "length": len(stack),
            "sum": sum(stack),
            "average": sum(stack) / len(stack),
            "min": min(stack),
            "max": max(stack),
            "value_distribution": {i: stack.count(i) for i in range(1, 7)},
            "possible_max_total": sum(stack),
            "expected_moves": len(stack) // 2
        }
    
    @staticmethod
    def create_test_stacks() -> dict:
        test_stacks = {
            "simple_short": [3, 5, 2, 6],  # 4 values, simple case
            "winning_21": [6, 6, 6, 3, 2, 4],  # Can reach exactly 21
            "bust_early": [6, 6, 6, 6, 1, 1],  # Likely to bust early
            "balanced_medium": StackManager.generate_balanced_stack(12),
            "all_sixes": [6] * 10,  # Extreme case
            "all_ones": [1] * 10,  # Another extreme
            "alternating": [1, 6, 2, 5, 3, 4, 1, 6, 2, 5],  # Alternating pattern
            "increasing": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6],  # Increasing pattern
        }
        
        for name, stack in test_stacks.items():
            StackManager.save_stack(stack, f"test_{name}.json")
        
        return test_stacks
    
    @staticmethod
    def validate_stack(stack: List[int]) -> Tuple[bool, str]:
        if not stack:
            return False, "Stack cannot be empty"
        
        if len(stack) < 2:
            return False, "Stack must have at least 2 values for dual-value game"
        
        for value in stack:
            if not 1 <= value <= 6:
                return False, f"Value {value} is not between 1 and 6"
        
        return True, "Valid stack"
    
    @staticmethod
    def create_stack_from_string(stack_str: str) -> List[int]:
        try:
            stack = [int(x.strip()) for x in stack_str.split(',')]
            valid, message = StackManager.validate_stack(stack)
            if not valid:
                raise ValueError(message)
            return stack
        except ValueError as e:
            raise ValueError(f"Invalid stack string: {stack_str}. Error: {e}")


# Example usage
if __name__ == "__main__":
    mgr = StackManager()
    
    stack = mgr.generate_random_stack(10)
    print(f"Random stack: {stack}")
    analysis = mgr.analyze_stack(stack)
    print(f"Analysis: {json.dumps(analysis, indent=2)}")
    
    test_stacks = mgr.create_test_stacks()
    print(f"\nCreated {len(test_stacks)} test stacks")