
from typing import Tuple, Optional
from src.game.game_state import GameState
from src.algorithms.alphabeta import AlphaBetaSolver

class IterativeDeepeningSolver:
    def __init__(self, time_limit: float = 1.0):
        self.time_limit = time_limit
        self.stats = {}