import sys
from typing import List, Optional, Dict, Any
from src.game.game_state import GameState


class TreeVisualizer:
    def __init__(self, max_depth: int = 4, max_children: int = 2, width: int = 80):

        self.max_depth = max_depth
        self.max_children = max_children
        self.width = width
        self.colors = {
            'MAX': '\033[94m',      # Blue
            'MIN': '\033[91m',      # Red
            'WIN': '\033[92m',      # Green
            'LOSE': '\033[91m',     # Red
            'PATH': '\033[93m',     # Yellow
            'TERMINAL': '\033[95m', # Magenta
            'RESET': '\033[0m'      # Reset
        }
    
    def visualize_tree(self, root_state: GameState, highlight_path: Optional[List[GameState]] = None) -> str:
        if highlight_path is None:
            highlight_path = []
        
        path_states = {id(state): state for state in highlight_path}
        
        output = []
        output.append(self._create_header("GAME DECISION TREE"))
        output.append(f"Max depth shown: {self.max_depth}")
        output.append(f"Branching factor: {self.max_children}")
        output.append("")
        
        tree_lines = self._generate_tree_lines(root_state, path_states, depth=0, prefix="")
        output.extend(tree_lines)
        
        output.append("")
        output.append(self._create_legend())
        
        return "\n".join(output)
    
    def _generate_tree_lines(self, state: GameState, path_states: Dict[int, GameState], 
                           depth: int, prefix: str) -> List[str]:
        """Recursively generate tree lines."""
        lines = []
        
        if depth > self.max_depth:
            return lines
        
        is_in_path = id(state) in path_states
        
        node_str = self._format_node(state, is_in_path)
        
        if depth > 0:
            lines.append(f"{prefix}{node_str}")
        else:
            lines.append(node_str)
        
        children = self._get_children_for_display(state)
        
        # Recursively process children
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            
            child_prefix = prefix + ("    " if depth == 0 else "│   " if not is_last else "    ")
            
            connector = "└── " if is_last else "├── "
            if depth > 0:
                lines.append(f"{prefix}{connector}")
            
            # Recursively process child
            child_lines = self._generate_tree_lines(
                child, path_states, depth + 1, 
                prefix + ("    " if is_last else "│   ")
            )
            lines.extend(child_lines)
        
        return lines
    
    def _format_node(self, state: GameState, highlight: bool = False) -> str:
        player_color = self.colors['MAX'] if state.is_maximizing else self.colors['MIN']
        player_text = "MAX" if state.is_maximizing else "MIN"
        
        is_terminal = state.is_terminal
        
        status = ""
        if is_terminal:
            if state.total == 21:
                status = f"{self.colors['WIN']}WIN{self.colors['RESET']}"
            elif state.total > 21:
                status = f"{self.colors['LOSE']}LOSE{self.colors['RESET']}"
            else:
                status = f"{self.colors['TERMINAL']}END{self.colors['RESET']}"
        
        move_info = ""
        if state.move_from_parent:
            value_taken, value_discarded, _ = state.move_from_parent
            move_info = f"Move: {value_taken} (discard {value_discarded}) | "
        
        value_str = ""
        if state.value is not None:
            value_str = f"Value: {state.value:+.1f} | "
        
        highlight_prefix = f"{self.colors['PATH']}▶ " if highlight else "  "
        
        node_parts = [
            f"{highlight_prefix}{player_color}{player_text}{self.colors['RESET']}",
            f"Total: {state.total:2d}",
            f"StackIdx: {state.stack_index}",
            move_info,
            value_str,
            status
        ]
        
        node_str = " | ".join(filter(None, node_parts))
        
        return node_str
    
    def _get_children_for_display(self, state: GameState) -> List[GameState]:
        if state.is_terminal:
            return []
        

        if hasattr(state, 'children') and state.children:
            children = state.children
        
        # Sort children by value for better display
        children = sorted(
            state.children, 
            key=lambda x: x.value if x.value is not None else x.evaluate(), reverse=state.is_maximizing  # Best first for current player
        )
        
        return children[:self.max_children]
    
    def _create_header(self, title: str) -> str:
        border = "=" * self.width
        padding = (self.width - len(title) - 2) // 2
        title_line = f"{' ' * padding} {title} {' ' * padding}"
        return f"\n{border}\n{title_line}\n{border}"
    
    def _create_legend(self) -> str:
        legend = [
            "LEGEND:",
            f"  {self.colors['MAX']}MAX{self.colors['RESET']}: AI player (maximizing)",
            f"  {self.colors['MIN']}MIN{self.colors['RESET']}: Opponent (minimizing)",
            f"  {self.colors['PATH']}▶ {self.colors['RESET']}: On optimal path",
            f"  {self.colors['WIN']}WIN{self.colors['RESET']}: Winning terminal state",
            f"  {self.colors['LOSE']}LOSE{self.colors['RESET']}: Losing terminal state",
            f"  {self.colors['TERMINAL']}END{self.colors['RESET']}: Terminal (no win/loss)",
            "  │   : Branch continues",
            "  └── : Last branch",
            "  ├── : Branch continues below"
        ]
        return "\n".join(legend)
    
    def export_tree_dot(self, root_state: GameState, filename: str, 
                       highlight_path: Optional[List[GameState]] = None) -> None:

        if highlight_path is None:
            highlight_path = []
        
        path_states = {id(state): state for state in highlight_path}
        
        dot_lines = [
            "digraph GameTree {",
            "  rankdir=TB;",
            "  node [shape=rectangle, style=filled];",
            "  edge [fontsize=10];",
            ""
        ]
        
        # Add nodes and edges recursively
        self._add_dot_nodes(root_state, path_states, dot_lines, set())
        
        dot_lines.append("}")
        
        # Write to file
        with open(filename, 'w') as f:
            f.write("\n".join(dot_lines))
        
        print(f"Tree exported to {filename}")
        print("To visualize: dot -Tpng tree.dot -o tree.png")
    
    def _add_dot_nodes(self, state: GameState, path_states: Dict[int, GameState], 
                      dot_lines: List[str], visited: set) -> None:
        node_id = id(state)
        
        # Avoid infinite recursion
        if node_id in visited:
            return
        visited.add(node_id)
        
        # Determine node properties
        fillcolor = "lightblue" if state.is_maximizing else "lightcoral"
        if state.is_terminal:
            if state.total == 21:
                fillcolor = "lightgreen"
            elif state.total > 21:
                fillcolor = "red"
            else:
                fillcolor = "gray"
        
        # Highlight if in solution path
        if id(state) in path_states:
            fillcolor = "gold"
            penwidth = "3"
        else:
            penwidth = "1"
        
        # Create node label
        label_parts = []
        label_parts.append(f"Player: {'MAX' if state.is_maximizing else 'MIN'}")
        label_parts.append(f"Total: {state.total}")
        
        if state.move_from_parent:
            val_taken, val_discarded, _ = state.move_from_parent
            label_parts.append(f"Move: {val_taken} (discard {val_discarded})")
        
        if state.value is not None:
            label_parts.append(f"Value: {state.value:.1f}")
        
        if state.is_terminal:
            if state.total == 21:
                label_parts.append("WIN!")
            elif state.total > 21:
                label_parts.append("LOSE")
            else:
                label_parts.append("END")
        
        label = "\\n".join(label_parts)
        
        # Add node to DOT
        dot_lines.append(f'  n{node_id} [label="{label}", fillcolor="{fillcolor}", '
                        f'style="filled", penwidth={penwidth}];')
        
        # Process children
        for child in getattr(state, 'children', []):
            child_id = id(child)
            
            # Add edge
            edge_label = f"{child.move_from_parent[0]}" if child.move_from_parent else ""
            dot_lines.append(f'  n{node_id} -> n{child_id} [label="{edge_label}"];')
            
            # Recursively process child
            self._add_dot_nodes(child, path_states, dot_lines, visited)
    
    def print_comparison(self, state1: GameState, state2: GameState, title: str = "COMPARISON") -> str:
        """Print comparison between two game states."""
        output = []
        output.append(self._create_header(title))
        output.append("")
        
        output.append("STATE 1:")
        output.append(self._format_node(state1))
        output.append("")
        
        output.append("STATE 2:")
        output.append(self._format_node(state2))
        output.append("")
        
        output.append("COMPARISON:")
        comparisons = []
        
        if state1.total != state2.total:
            comparisons.append(f"Total: {state1.total} vs {state2.total}")
        
        if state1.is_maximizing != state2.is_maximizing:
            comparisons.append(f"Player: {'MAX' if state1.is_maximizing else 'MIN'} vs {'MAX' if state2.is_maximizing else 'MIN'}")
        
        if state1.value is not None and state2.value is not None:
            comparisons.append(f"Value: {state1.value:.1f} vs {state2.value:.1f} (diff: {state1.value - state2.value:.1f})")
        
        if state1.is_terminal != state2.is_terminal:
            comparisons.append(f"Terminal: {state1.is_terminal} vs {state2.is_terminal}")
        
        if comparisons:
            output.extend([f"  • {comp}" for comp in comparisons])
        else:
            output.append("  States are identical")
        
        return "\n".join(output)


# Example usage
if __name__ == "__main__":
    from src.game.stack_manager import StackManager
    from src.algorithms.minimax import MinimaxSolver
    
    # Create a simple game
    stack = [3, 5, 2, 6]
    initial_state = GameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
    
    # Solve to generate children
    solver = MinimaxSolver(depth_limit=3)
    value, _ = solver.solve(initial_state)
    
    # Create visualizer
    visualizer = TreeVisualizer(max_depth=3, max_children=2)
    
    # Visualize tree
    tree_text = visualizer.visualize_tree(initial_state)
    print(tree_text)
    
    # Export to DOT
    visualizer.export_tree_dot(initial_state, "game_tree.dot")