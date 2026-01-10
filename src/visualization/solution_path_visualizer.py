from typing import List
from src.game.game_state import GameState


class SolutionPathTreeVisualizer:
    """
    Visualiza APENAS o caminho solução (minimax / alpha-beta)
    em formato de árvore linear.
    """

    def __init__(self, width: int = 80):
        self.width = width
        self.colors = {
            'MAX': '\033[94m',
            'MIN': '\033[91m',
            'WIN': '\033[92m',
            'LOSE': '\033[91m',
            'PATH': '\033[93m',
            'RESET': '\033[0m'
        }

    def visualize(self, path: List[GameState]) -> str:
        if not path:
            return "No solution path to display."

        output = []
        output.append(self._header("SOLUTION PATH TREE"))
        output.append("")

        for depth, state in enumerate(path):
            indent = "    " * depth
            connector = "└── " if depth > 0 else ""
            output.append(f"{indent}{connector}{self._format_node(state)}")

        output.append("")
        output.append(self._footer(path[-1]))
        return "\n".join(output)

    def _format_node(self, state: GameState) -> str:
        player = "MAX" if state.is_maximizing else "MIN"
        color = self.colors[player]

        move_info = ""
        if state.move_from_parent:
            taken, discarded, _ = state.move_from_parent
            move_info = f" | take {taken}, discard {discarded}"

        value_info = ""
        if state.value is not None:
            value_info = f" | value {state.value:+.1f}"

        terminal_info = ""
        if state.is_terminal:
            if state.total == 21:
                terminal_info = f" | {self.colors['WIN']}WIN{self.colors['RESET']}"
            elif state.total > 21:
                terminal_info = f" | {self.colors['LOSE']}LOSE{self.colors['RESET']}"

        return (
            f"{color}{player}{self.colors['RESET']} | "
            f"total {state.total}"
            f"{move_info}"
            f"{value_info}"
            f"{terminal_info}"
        )

    def _header(self, title: str) -> str:
        border = "=" * self.width
        pad = (self.width - len(title) - 2) // 2
        return f"{border}\n{' ' * pad} {title} {' ' * pad}\n{border}"

    def _footer(self, final_state: GameState) -> str:
        if final_state.total == 21:
            return f"{self.colors['WIN']}FINAL RESULT: WIN{self.colors['RESET']}"
        elif final_state.total > 21:
            return f"{self.colors['LOSE']}FINAL RESULT: LOSE{self.colors['RESET']}"
        return f"{self.colors['PATH']}FINAL RESULT: END{self.colors['RESET']}"
