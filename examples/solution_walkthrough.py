def demonstrate_solution_path():    
    # Use a stack with known optimal solution
    test_stack = [3, 5, 2, 6, 4, 1, 3, 2]
    
    solver = Stack21Solver(test_stack)
    
    print("="*70)
    print("STACK-BASED 21 SOLVER - SOLUTION PATH DEMONSTRATION")
    print("="*70)
    
    # Step 1: Solve the game
    solution_path = solver.solve(use_alpha_beta=True)
    
    # Step 2: Display the optimal path
    solver.display_solution()
    
    # Step 3: Show critical decision points
    print("\n" + "="*60)
    print("CRITICAL DECISION POINTS")
    print("="*60)
    
    for i, decision in enumerate(solver.tracker.decision_points[:5]):  # Show first 5
        print(f"\nDecision {i+1} (Depth {decision['depth']}):")
        print(f"  Player: {'MAX' if decision['is_maximizing'] else 'MIN'}")
        print(f"  Total: {decision['total']}")
        print(f"  Best move: Take {decision['best_move'][0] if decision['best_move'] else 'None'}")
        print(f"  Value: {decision['value']}")
        print(f"  Alpha/Beta: [{decision['alpha']}, {decision['beta']}]")
    
    # Step 4: Show pruning effectiveness
    print("\n" + "="*60)
    print("PRUNING ANALYSIS")
    print("="*60)
    
    total_nodes = solver.tracker.nodes_evaluated + solver.tracker.pruned_branches
    if total_nodes > 0:
        print(f"Total possible nodes (without pruning): {total_nodes:,}")
        print(f"Nodes actually evaluated: {solver.tracker.nodes_evaluated:,}")
        print(f"Nodes pruned: {solver.tracker.pruned_branches:,}")
        print(f"Pruning efficiency: {solver.tracker.pruned_branches/total_nodes:.2%}")
    
    # Step 5: Interactive exploration
    print("\n" + "="*60)
    print("INTERACTIVE EXPLORATION")
    print("="*60)
    
    print("\nAlternative moves analysis from initial state:")
    initial_state = solver.initial_state
    
    for move in initial_state.get_possible_moves():
        child = initial_state.apply_move(move)
        value = child.evaluate() if child.is_terminal else "Needs deeper analysis"
        print(f"  Move: Take {move[0]} (discard {move[1]}) → Total: {move[2]}, Value: {value}")

if __name__ == "__main__":
    demonstrate_solution_path()