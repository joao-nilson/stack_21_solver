class Stack21Solver:
    """Main solver that orchestrates everything."""
    
    def __init__(self, stack=None):
        self.stack = stack or self.generate_random_stack(10)
        self.initial_state = GameState(total=0, stack_index=0, stack=self.stack, is_maximizing=True)
        self.tracker = SolutionTracker()
        self.solution_path = None
        self.solution_summary = None
    
    def generate_random_stack(self, length):
        """Generate a random stack of dice values (1-6)."""
        import random
        return [random.randint(1, 6) for _ in range(length)]
    
    def solve(self, use_alpha_beta=True, depth_limit=None):
        """Solve the game and find optimal path."""
        print(f"Solving Stack-based 21 with stack: {self.stack}")
        print(f"Stack length: {len(self.stack)}")
        print(f"Using {'Alpha-Beta Pruning' if use_alpha_beta else 'Minimax'}")
        
        if use_alpha_beta:
            start_time = time.time()
            value, terminal_state = alphabeta_with_tracking(
                self.initial_state, 
                depth=0,
                alpha=float('-inf'),
                beta=float('inf'),
                is_maximizing=True,
                tracker=self.tracker,
                depth_limit=depth_limit
            )
            elapsed = time.time() - start_time
        else:
            # Implement basic minimax here
            pass
        
        # Reconstruct solution path
        self.solution_path = self.tracker.reconstruct_solution_path(self.initial_state, terminal_state)
        self.solution_summary = self.tracker.get_solution_summary()
        
        print(f"\nSolution found in {elapsed:.4f} seconds")
        print(f"Nodes evaluated: {self.tracker.nodes_evaluated}")
        print(f"Branches pruned: {self.tracker.pruned_branches}")
        print(f"Pruning efficiency: {self.tracker.pruned_branches/(self.tracker.nodes_evaluated + self.tracker.pruned_branches):.2%}")
        
        return self.solution_path
    
    def display_solution(self):
        """Display the solution path in human-readable format."""
        if not self.solution_path:
            print("No solution found. Run solve() first.")
            return
        
        print("\n" + "="*60)
        print("OPTIMAL SOLUTION PATH")
        print("="*60)
        
        for i, state in enumerate(self.solution_path):
            if i == 0:
                print(f"\nInitial State:")
            else:
                move = state.move_from_parent
                player = "MAX (AI)" if not state.is_maximizing else "MIN (Opponent)"
                print(f"\nTurn {i}: {player} plays")
                print(f"  Takes: {move[0]}, Discards: {move[1]}")
            
            print(f"  Total: {state.total}")
            if state.stack_index < len(state.stack):
                remaining = self.stack[state.stack_index:]
                print(f"  Remaining stack: {remaining}")
            
            if state.is_terminal:
                print(f"\n  TERMINAL STATE:")
                if state.total == 21:
                    winner = "MAX" if not state.is_maximizing else "MIN"
                    print(f"  {winner} WINS by reaching exactly 21!")
                elif state.total > 21:
                    loser = "MAX" if not state.is_maximizing else "MIN"
                    print(f"  {loser} LOSES by exceeding 21!")
                else:
                    print(f"  Game ended with total {state.total}")
                print(f"  Minimax value: {state.value}")
        
        # Display summary
        print("\n" + "="*60)
        print("SOLUTION SUMMARY")
        print("="*60)
        for key, value in self.solution_summary.items():
            if key != 'move_sequence':
                print(f"{key.replace('_', ' ').title()}: {value}")
    
    def visualize_decision_tree(self, max_depth=3):
        """Visualize the game tree up to specified depth."""
        from visualization.tree_visualizer import visualize_tree
        
        visualize_tree(
            self.initial_state,
            max_depth=max_depth,
            highlight_path=self.solution_path
        )