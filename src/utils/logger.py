import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


class GameLogger:
    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    def __init__(self, name: str = "Stack21Solver", log_level: str = "INFO", 
                 log_to_file: bool = True, log_dir: str = "logs"):
        self.name = name
        self.log_level = self.LOG_LEVELS.get(log_level.upper(), logging.INFO)
        self.log_to_file = log_to_file
        self.log_dir = Path(log_dir)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        self.logger.handlers.clear()
        
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        if self.log_to_file:
            self._setup_file_handler(detailed_formatter)
        
        self.logger.propagate = False
        
        self.log_entries = []
        
        self.logger.info(f"Logger initialized for {name} at level {log_level}")
    
    def _setup_file_handler(self, formatter: logging.Formatter) -> None:
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = self.log_dir / f"stack21_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.current_log_file = log_filename
        self.logger.info(f"Logging to file: {log_filename}")
    
    def log_game_start(self, stack: list, algorithm: str, depth_limit: Optional[int] = None) -> None:
        self.logger.info("=" * 60)
        self.logger.info("GAME START")
        self.logger.info("=" * 60)
        self.logger.info(f"Stack: {stack}")
        self.logger.info(f"Stack length: {len(stack)}")
        self.logger.info(f"Algorithm: {algorithm}")
        if depth_limit:
            self.logger.info(f"Depth limit: {depth_limit}")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    def log_move(self, turn: int, player: str, move: tuple, total: int, 
                remaining_stack: list, evaluation: Optional[float] = None) -> None:
        move_str = f"Turn {turn}: {player} takes {move[0]}, discards {move[1]} -> Total: {total}"
        
        if evaluation is not None:
            move_str += f" (Eval: {evaluation:.1f})"
        
        self.logger.info(move_str)
        
        self.log_entries.append({
            'timestamp': datetime.now().isoformat(),
            'turn': turn,
            'player': player,
            'move': move,
            'total': total,
            'remaining_stack': remaining_stack.copy() if remaining_stack else [],
            'evaluation': evaluation
        })
    
    def log_decision(self, state: Dict[str, Any], best_move: tuple, alternatives: list) -> None:
        self.logger.debug(f"Decision at total={state.get('total', 0)}:")
        self.logger.debug(f"  Best move: Take {best_move[0]}, discard {best_move[1]}")
        self.logger.debug(f"  Alternatives: {len(alternatives)}")
        
        for i, alt in enumerate(alternatives[:3]):  # Log first 3 alternatives
            self.logger.debug(f"    Alt {i+1}: Take {alt[0]}, discard {alt[1]} -> Total: {alt[2]}")
    
    def log_pruning(self, alpha: float, beta: float, pruned_branches: int, depth: int) -> None:
        self.logger.debug(f"Pruning at depth {depth}: α={alpha:.1f}, β={beta:.1f}, "
                         f"pruned {pruned_branches} branches")
    
    def log_performance(self, stats: Dict[str, Any]) -> None:
        self.logger.info("=" * 60)
        self.logger.info("PERFORMANCE STATISTICS")
        self.logger.info("=" * 60)
        
        for key, value in stats.items():
            if isinstance(value, float):
                if 'efficiency' in key or 'percentage' in key:
                    self.logger.info(f"{key}: {value:.2%}")
                elif 'time' in key:
                    self.logger.info(f"{key}: {value:.4f}s")
                elif 'memory' in key:
                    self.logger.info(f"{key}: {value:.2f}MB")
                else:
                    self.logger.info(f"{key}: {value:.2f}")
            elif isinstance(value, int):
                self.logger.info(f"{key}: {value:,}")
            else:
                self.logger.info(f"{key}: {value}")
    
    def log_solution(self, path: list, winner: Optional[str] = None) -> None:
        self.logger.info("=" * 60)
        self.logger.info("SOLUTION FOUND")
        self.logger.info("=" * 60)
        
        if winner:
            self.logger.info(f"Winner: {winner}")
        
        self.logger.info(f"Total moves: {len(path) - 1}")
        self.logger.info(f"Final total: {path[-1].total if path else 'N/A'}")
        
        self.logger.info("Move sequence:")
        for i, state in enumerate(path):
            if i == 0:
                continue
            if hasattr(state, 'move_from_parent') and state.move_from_parent:
                move = state.move_from_parent
                player = "MAX" if not state.is_maximizing else "MIN"  # Player who made the move
                self.logger.info(f"  Turn {i}: {player} - Take {move[0]}, discard {move[1]} -> Total: {state.total}")
    
    def log_error(self, error: Exception, context: Optional[str] = None) -> None:
        if context:
            self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
        else:
            self.logger.error(f"Error: {str(error)}", exc_info=True)
    
    def log_warning(self, warning: str, context: Optional[str] = None) -> None:
        if context:
            self.logger.warning(f"Warning in {context}: {warning}")
        else:
            self.logger.warning(f"Warning: {warning}")
    
    def save_log_analysis(self, filename: Optional[str] = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.log_dir / f"log_analysis_{timestamp}.json"
        else:
            filename = Path(filename)
        
        analysis = {
            'log_entries': self.log_entries,
            'summary': self._generate_log_summary(),
            'timestamp': datetime.now().isoformat(),
            'logger_name': self.name,
            'log_level': logging.getLevelName(self.log_level)
        }
        
        # Ensure directory exists
        filename.parent.mkdir(exist_ok=True, parents=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        self.logger.info(f"Log analysis saved to: {filename}")
        return str(filename)
    
    def _generate_log_summary(self) -> Dict[str, Any]:
        if not self.log_entries:
            return {}
        
        # Count moves by player
        max_moves = sum(1 for entry in self.log_entries if entry['player'] == 'MAX')
        min_moves = sum(1 for entry in self.log_entries if entry['player'] == 'MIN')
        
        # Calculate averages
        evaluations = [e['evaluation'] for e in self.log_entries if e['evaluation'] is not None]
        totals = [e['total'] for e in self.log_entries]
        
        summary = {
            'total_moves_logged': len(self.log_entries),
            'max_moves': max_moves,
            'min_moves': min_moves,
            'average_evaluation': sum(evaluations) / len(evaluations) if evaluations else None,
            'max_total': max(totals) if totals else None,
            'min_total': min(totals) if totals else None,
            'final_total': self.log_entries[-1]['total'] if self.log_entries else None
        }
        
        return summary
    
    def set_level(self, level: str) -> None:
        new_level = self.LOG_LEVELS.get(level.upper(), logging.INFO)
        self.log_level = new_level
        self.logger.setLevel(new_level)
        
        for handler in self.logger.handlers:
            handler.setLevel(new_level)
        
        self.logger.info(f"Log level changed to: {level}")
    
    def get_logger(self) -> logging.Logger:
        return self.logger
    
    def create_sub_logger(self, name: str) -> 'GameLogger':
        sub_logger_name = f"{self.name}.{name}"
        return GameLogger(
            name=sub_logger_name,
            log_level=logging.getLevelName(self.log_level),
            log_to_file=self.log_to_file,
            log_dir=str(self.log_dir)
        )


_global_logger: Optional[GameLogger] = None


def setup_global_logger(log_level: str = "INFO", log_to_file: bool = True) -> GameLogger:
    global _global_logger
    
    if _global_logger is None:
        _global_logger = GameLogger(
            name="Stack21Global",
            log_level=log_level,
            log_to_file=log_to_file,
            log_dir="logs"
        )
    
    return _global_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    if _global_logger is None:
        setup_global_logger()
    
    if name:
        return _global_logger.create_sub_logger(name).get_logger()
    
    return _global_logger.get_logger()


def log_function_call(logger: Optional[GameLogger] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if logger is None:
                func_logger = get_logger(func.__module__)
            else:
                func_logger = logger.get_logger()
            
            func_logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                
                func_logger.debug(f"{func.__name__} returned: {result}")
                
                return result
            except Exception as e:
                func_logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Setup logger
    logger = GameLogger(log_level="DEBUG", log_to_file=False)
    
    # Test logging
    logger.log_game_start([1, 2, 3, 4, 5, 6], "Minimax", depth_limit=5)
    
    # Log some moves
    logger.log_move(1, "MAX", (3, 5), 3, [2, 6, 4, 1], evaluation=42.5)
    logger.log_move(2, "MIN", (2, 6), 5, [4, 1], evaluation=-12.3)
    
    # Log decision
    logger.log_decision(
        {'total': 14, 'player': 'MAX'},
        (4, 1),
        [(1, 4, 15), (6, 2, 20)]
    )
    
    # Log pruning
    logger.log_pruning(alpha=10.5, beta=20.3, pruned_branches=3, depth=2)
    
    # Log performance
    logger.log_performance({
        'execution_time': 0.1234,
        'nodes_evaluated': 12345,
        'memory_usage': 12.34
    })
    
    # Log solution
    class MockState:
        def __init__(self, total, move=None, is_max=True):
            self.total = total
            self.move_from_parent = move
            self.is_maximizing = is_max
    
    path = [
        MockState(0),
        MockState(3, (3, 5), False),
        MockState(5, (2, 6), True),
        MockState(21, (6, 4), False)
    ]
    
    logger.log_solution(path, winner="MAX")
    
    # Save analysis
    analysis_file = logger.save_log_analysis("test_log_analysis.json")
    print(f"Log analysis saved to: {analysis_file}")