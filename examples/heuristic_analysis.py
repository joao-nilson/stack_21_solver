import sys
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.game.stack_manager import StackManager
from src.game.game_state import GameState
from src.algorithms.alphabeta import AlphaBetaSolver


class HeuristicAnalysis:
    
    def __init__(self):
        self.results = {}
        self.visualizations_dir = Path("heuristic_analysis")
        self.visualizations_dir.mkdir(exist_ok=True)
    
    def define_heuristic_families(self):
        
        # Family 1: Distance-based heuristics
        def distance_heuristic_base(state, weight=1.0):
            if state.total == 21:
                return 10000 if state.is_maximizing else -10000
            if state.total > 21:
                return -10000 if state.is_maximizing else 10000
            
            distance = 21 - state.total
            score = 1000 - (distance * 50 * weight)
            return score if state.is_maximizing else -score
        
        # Family 2: Aggression-based heuristics
        def aggression_heuristic_base(state, aggression=1.0):
            if state.total == 21:
                return 10000 if state.is_maximizing else -10000
            if state.total > 21:
                return -10000 if state.is_maximizing else 10000
            
            # Higher aggression means more reward for high totals
            score = state.total * (10 * aggression)
            if 15 <= state.total <= 20:
                score += (state.total - 14) * (100 * aggression)
            return score if state.is_maximizing else -score
        
        # Family 3: Risk-based heuristics
        def risk_heuristic_base(state, risk_aversion=1.0):
            if state.total == 21:
                return 10000 if state.is_maximizing else -10000
            if state.total > 21:
                return -50000 * risk_aversion if state.is_maximizing else 50000 * risk_aversion
            
            # Higher risk_aversion means stronger penalty for being close to bust
            remaining_to_bust = 21 - state.total
            if remaining_to_bust < 4:
                # Very risk-averse when close to busting
                score = state.total * (5 / risk_aversion)
            else:
                score = state.total * 30
            
            return score if state.is_maximizing else -score
        
        # Create variations
        self.heuristic_families = {
            "distance": {
                "low": lambda s: distance_heuristic_base(s, weight=0.5),
                "medium": lambda s: distance_heuristic_base(s, weight=1.0),
                "high": lambda s: distance_heuristic_base(s, weight=2.0)
            },
            "aggression": {
                "low": lambda s: aggression_heuristic_base(s, aggression=0.5),
                "medium": lambda s: aggression_heuristic_base(s, aggression=1.0),
                "high": lambda s: aggression_heuristic_base(s, aggression=2.0)
            },
            "risk": {
                "low": lambda s: risk_heuristic_base(s, risk_aversion=0.5),  # Risk-taking
                "medium": lambda s: risk_heuristic_base(s, risk_aversion=1.0),  # Balanced
                "high": lambda s: risk_heuristic_base(s, risk_aversion=2.0)  # Risk-averse
            }
        }
        
        return self.heuristic_families
    
    def run_analysis(self, stack, family_name, variations):
        print(f"\nAnalyzing {family_name} heuristic family...")
        
        results = {}
        
        for variation_name, heuristic_func in variations.items():
            print(f"  Testing {variation_name} variation...")
            
            class CustomGameState(GameState):
                def evaluate(self):
                    return heuristic_func(self)
            
            initial_state = CustomGameState(total=0, stack_index=0, stack=stack, is_maximizing=True)
            
            solver = AlphaBetaSolver(depth_limit=6)
            value, terminal_state = solver.solve(initial_state)
            
            path = solver.get_solution_path(initial_state)
            
            # Collect metrics
            terminal = path[-1] if path else None
            moves = []
            for state in path[1:]:
                if state.move_from_parent:
                    moves.append(state.move_from_parent[0])
            
            results[variation_name] = {
                "value": value,
                "final_total": terminal.total if terminal else None,
                "moves": len(moves),
                "avg_move": sum(moves) / len(moves) if moves else 0,
                "max_move": max(moves) if moves else 0,
                "min_move": min(moves) if moves else 0,
                "nodes_evaluated": solver.tracker.nodes_evaluated,
                "pruned_branches": solver.tracker.pruned_branches,
                "path": [(state.total, state.is_maximizing) for state in path] if path else []
            }
        
        return results
    
    def analyze_multiple_stacks(self):
        manager = StackManager()
        
        test_stacks = {
            "balanced": manager.generate_balanced_stack(12),
            "high_bias": [6, 5, 6, 4, 6, 3, 5, 4, 5, 3, 4, 2],
            "low_bias": [1, 2, 1, 3, 1, 4, 2, 3, 2, 4, 3, 4],
            "alternating": [1, 6, 2, 5, 3, 4, 4, 3, 5, 2, 6, 1],
            "extreme": [6, 6, 6, 6, 1, 1, 1, 1, 6, 6, 1, 1]
        }
        
        all_results = {}
        
        for stack_name, stack in test_stacks.items():
            print(f"\n{'='*80}")
            print(f"STACK: {stack_name.upper()}")
            print(f"Stack: {stack}")
            print(f"{'='*80}")
            
            stack_results = {}
            
            for family_name, variations in self.heuristic_families.items():
                family_results = self.run_analysis(stack, family_name, variations)
                stack_results[family_name] = family_results
            
            all_results[stack_name] = stack_results
            
            self.generate_stack_visualizations(stack_name, stack, stack_results)
        
        self.save_results(all_results)
        
        self.generate_comparative_analysis(all_results)
        
        return all_results
    
    def generate_stack_visualizations(self, stack_name, stack, results):
        stack_dir = self.visualizations_dir / stack_name
        stack_dir.mkdir(exist_ok=True)
        
        # 1. Final Total Comparison
        plt.figure(figsize=(12, 8))
        
        families = list(results.keys())
        variations = ["low", "medium", "high"]
        
        x = np.arange(len(families))
        width = 0.25
        
        for i, variation in enumerate(variations):
            totals = []
            for family in families:
                if variation in results[family]:
                    totals.append(results[family][variation]["final_total"])
                else:
                    totals.append(0)
            
            plt.bar(x + i*width - width, totals, width, label=variation)
        
        plt.xlabel('Heuristic Family')
        plt.ylabel('Final Total')
        plt.title(f'Final Total Comparison - {stack_name}')
        plt.xticks(x, families)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(stack_dir / f"{stack_name}_final_totals.png")
        plt.close()
        
        # 2. Move Statistics
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        metrics = ["avg_move", "max_move", "min_move", "nodes_evaluated"]
        metric_names = ["Average Move", "Max Move", "Min Move", "Nodes Evaluated"]
        
        for idx, (metric, name) in enumerate(zip(metrics, metric_names)):
            ax = axes[idx]
            
            for variation in variations:
                values = []
                for family in families:
                    if variation in results[family]:
                        values.append(results[family][variation][metric])
                    else:
                        values.append(0)
                
                ax.plot(families, values, marker='o', label=variation)
            
            ax.set_xlabel('Heuristic Family')
            ax.set_ylabel(name)
            ax.set_title(f'{name} by Heuristic')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(stack_dir / f"{stack_name}_move_stats.png")
        plt.close()
        
        # 3. Path Comparison
        plt.figure(figsize=(14, 8))
        
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']
        color_idx = 0
        
        for family in families:
            for variation in variations:
                if variation in results[family]:
                    path_data = results[family][variation]["path"]
                    if path_data:
                        totals = [state[0] for state in path_data]
                        moves = list(range(len(totals)))
                        
                        plt.plot(moves, totals, marker='o', 
                                label=f"{family}-{variation}",
                                color=colors[color_idx % len(colors)],
                                alpha=0.7)
                        color_idx += 1
        
        plt.axhline(y=21, color='r', linestyle='--', alpha=0.5, label='Target (21)')
        plt.xlabel('Move Number')
        plt.ylabel('Total')
        plt.title(f'Solution Paths Comparison - {stack_name}')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(stack_dir / f"{stack_name}_paths.png", bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to: {stack_dir}/")
    
    def save_results(self, all_results):
        output_file = self.visualizations_dir / "heuristic_analysis_results.json"
        
        # Convert to serializable format
        serializable_results = {}
        for stack_name, stack_results in all_results.items():
            serializable_results[stack_name] = {}
            for family_name, family_results in stack_results.items():
                serializable_results[stack_name][family_name] = {}
                for variation_name, variation_results in family_results.items():
                    # Convert path to list of tuples
                    path = variation_results.get("path", [])
                    serializable_path = []
                    for total, is_max in path:
                        serializable_path.append({
                            "total": total,
                            "player": "MAX" if is_max else "MIN"
                        })
                    
                    serializable_results[stack_name][family_name][variation_name] = {
                        "value": variation_results.get("value"),
                        "final_total": variation_results.get("final_total"),
                        "moves": variation_results.get("moves"),
                        "avg_move": variation_results.get("avg_move"),
                        "max_move": variation_results.get("max_move"),
                        "min_move": variation_results.get("min_move"),
                        "nodes_evaluated": variation_results.get("nodes_evaluated"),
                        "pruned_branches": variation_results.get("pruned_branches"),
                        "path": serializable_path
                    }
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
    
    def generate_comparative_analysis(self, all_results):
        print(f"\n{'='*80}")
        print("COMPARATIVE ANALYSIS ACROSS ALL STACKS")
        print(f"{'='*80}")
        
        comparison_data = {
            "best_21_reachers": [],
            "most_efficient": [],
            "safest_play": []
        }
        
        for stack_name, stack_results in all_results.items():
            # Find best for reaching 21
            best_distance = float('inf')
            best_config_21 = None
            
            # Find most efficient (nodes evaluated)
            best_efficiency = float('inf')
            best_config_eff = None
            
            # Find safest (avoid bust)
            best_safety = -float('inf')
            best_config_safe = None
            
            for family_name, family_results in stack_results.items():
                for variation_name, results in family_results.items():
                    final_total = results.get("final_total", 0)
                    distance = abs(21 - final_total)
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_config_21 = (family_name, variation_name, final_total)
                    
                    efficiency = results.get("nodes_evaluated", float('inf'))
                    if efficiency < best_efficiency:
                        best_efficiency = efficiency
                        best_config_eff = (family_name, variation_name, efficiency)
                    
                    if final_total <= 21 and final_total > best_safety:
                        best_safety = final_total
                        best_config_safe = (family_name, variation_name, final_total)
            
            if best_config_21:
                comparison_data["best_21_reachers"].append({
                    "stack": stack_name,
                    "heuristic": f"{best_config_21[0]}-{best_config_21[1]}",
                    "final_total": best_config_21[2],
                    "distance_from_21": best_distance
                })
            
            if best_config_eff:
                comparison_data["most_efficient"].append({
                    "stack": stack_name,
                    "heuristic": f"{best_config_eff[0]}-{best_config_eff[1]}",
                    "nodes_evaluated": best_config_eff[2]
                })
            
            if best_config_safe:
                comparison_data["safest_play"].append({
                    "stack": stack_name,
                    "heuristic": f"{best_config_safe[0]}-{best_config_safe[1]}",
                    "final_total": best_config_safe[2]
                })
        
        # Print analysis
        print("\n1. BEST FOR REACHING 21:")
        print("-" * 80)
        for item in sorted(comparison_data["best_21_reachers"], key=lambda x: x["distance_from_21"]):
            print(f"  Stack: {item['stack']:15} Heuristic: {item['heuristic']:20} "
                  f"Total: {item['final_total']:3} (Distance: {item['distance_from_21']})")
        
        print("\n2. MOST EFFICIENT (LEAST NODES EVALUATED):")
        print("-" * 80)
        for item in sorted(comparison_data["most_efficient"], key=lambda x: x["nodes_evaluated"]):
            print(f"  Stack: {item['stack']:15} Heuristic: {item['heuristic']:20} "
                  f"Nodes: {item['nodes_evaluated']:,}")
        
        print("\n3. SAFEST PLAY (HIGHEST TOTAL WITHOUT BUSTING):")
        print("-" * 80)
        for item in sorted(comparison_data["safest_play"], key=lambda x: x["final_total"], reverse=True):
            print(f"  Stack: {item['stack']:15} Heuristic: {item['heuristic']:20} "
                  f"Total: {item['final_total']}")
        
        # Generate summary visualization
        self.generate_summary_visualization(comparison_data)
    

    def blocking_heuristic(state, blocking_weight=1.5):
        
        
        if state.is_terminal:
            if state.total == 21: return 10000 if state.is_maximizing else -10000
            if state.total > 21: return -10000 if state.is_maximizing else 10000
            return state.total if state.is_maximizing else -state.total

        my_score = (21 - abs(21 - state.total)) * 10

        opponent_best_option = -float('inf')
        moves = state.get_possible_moves()

        bad_moves_for_opponent = 0
        total_moves = len(moves)

        for move in moves:
            new_total = move[2]
            dist = abs(21 - new_total)

        if new_total > 21:
            bad_moves_for_opponent += 1

        elif new_total == 21:
            opponent_best_option = 1000


        trap_score = (bad_moves_for_opponent / total_moves) * 500 * blocking_weight
    
        final_score = my_score + trap_score
    
        return final_score if state.is_maximizing else -final_score

    def generate_summary_visualization(self, comparison_data):
        fig, axes = plt.subplots(3, 1, figsize=(14, 15))
        
        # Plot 1: Best for reaching 21
        ax1 = axes[0]
        items = comparison_data["best_21_reachers"]
        x = [f"{item['stack']}\n{item['heuristic']}" for item in items]
        distances = [item["distance_from_21"] for item in items]
        
        bars = ax1.bar(x, distances, color='skyblue')
        ax1.set_ylabel('Distance from 21')
        ax1.set_title('Best Heuristics for Reaching 21 (Lower is Better)')
        ax1.tick_params(axis='x', rotation=45)
        
        for bar, distance in zip(bars, distances):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{distance}', ha='center', va='bottom')
        
        # Plot 2: Most efficient
        ax2 = axes[1]
        items = comparison_data["most_efficient"]
        x = [f"{item['stack']}\n{item['heuristic']}" for item in items]
        nodes = [item["nodes_evaluated"] for item in items]
        
        bars = ax2.bar(x, nodes, color='lightgreen')
        ax2.set_ylabel('Nodes Evaluated')
        ax2.set_title('Most Efficient Heuristics (Lower is Better)')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, node_count in zip(bars, nodes):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{node_count:,}', ha='center', va='bottom', fontsize=8)
        
        # Plot 3: Safest play
        ax3 = axes[2]
        items = comparison_data["safest_play"]
        x = [f"{item['stack']}\n{item['heuristic']}" for item in items]
        totals = [item["final_total"] for item in items]
        
        bars = ax3.bar(x, totals, color='lightcoral')
        ax3.axhline(y=21, color='r', linestyle='--', alpha=0.5, label='Target (21)')
        ax3.set_ylabel('Final Total')
        ax3.set_title('Safest Heuristics (Higher is Better, but ≤21)')
        ax3.tick_params(axis='x', rotation=45)
        ax3.legend()
        
        for bar, total in zip(bars, totals):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{total}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(self.visualizations_dir / "comparative_summary.png", dpi=150)
        plt.close()
        
        print(f"\nSummary visualization saved to: {self.visualizations_dir}/comparative_summary.png")

def main():
    print(f"\n{'='*80}")
    print("HEURISTIC ANALYSIS - DEEP DIVE")
    print("Analyzing how different heuristics affect solution paths")
    print(f"{'='*80}")
    
    analyzer = HeuristicAnalysis()
    
    analyzer.define_heuristic_families()
    
    print("\nStarting comprehensive heuristic analysis...")
    results = analyzer.analyze_multiple_stacks()
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*80}")
    print("\nGenerated files:")
    print(f"  • heuristic_analysis/heuristic_analysis_results.json - All analysis data")
    print(f"  • heuristic_analysis/comparative_summary.png - Summary visualization")
    print(f"  • heuristic_analysis/[stack_name]/ - Stack-specific visualizations")
    
    return results


if __name__ == "__main__":
    try:
        results = main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()