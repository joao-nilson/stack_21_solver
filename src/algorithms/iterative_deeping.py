import time
from typing import Tuple, Optional
from src.game.game_state import GameState
from src.algorithms.alphabeta import AlphaBetaSolver

class IterativeDeepeningSolver:
    def __init__(self, time_limit: float = 1.0):
        self.time_limit = time_limit
        self.stats = {}

    def solve(self, state: GameState) -> Tuple[float, Optional[GameState]]:
        start_time = time.time()
        best_value = -float('inf') if state.is_maximizing else float('inf')
        best_child = None
        
        current_depth = 1
        max_depth_reached = 0
        
        while True:
            # Verifica tempo
            if time.time() - start_time > self.time_limit:
                break
                
            # Cria um solver com limite fixo
            solver = AlphaBetaSolver(depth_limit=current_depth)
            
            try:
                val, child = solver.solve(state)
                
                # Se achou vitória forçada, retorna imediatamente
                if abs(val) >= 10000:
                    return val, child
                
                # Atualiza melhor resultado encontrado até agora
                best_value = val
                best_child = child
                max_depth_reached = current_depth
                
                # Se a busca terminou completamente (jogo acabou), para
                if child and child.is_terminal:
                    break
                    
                current_depth += 1
                
            except Exception as e:
                print(f"Erro na profundidade {current_depth}: {e}")
                break
        
        self.stats = {
            "algorithm": "iterative_deepening",
            "max_depth": max_depth_reached,
            "time_elapsed": time.time() - start_time
        }
        
        return best_value, best_child