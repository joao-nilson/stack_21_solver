#!/usr/bin/env python3
"""
Demonstration of Unified Configuration Management with existing codebase
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config_manager import ConfigManager
from config.experiment_config import ExperimentConfig
from examples.full_analysis import FixedGameAnalyzer
from examples.heuristic_analysis import HeuristicAnalysis
from examples.solution_path_demo import SolutionPathDemo


class ConfigIntegrationDemo:
    """Demonstrate configuration integration with existing tools"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.results = {}
    
    def demo_preset_loading(self):
        """Demonstrate loading and using presets"""
        print("\n" + "="*80)
        print("DEMO 1: PRESET CONFIGURATION LOADING")
        print("="*80)
        
        # List available presets
        presets = self.config_manager.get_preset_names()
        print(f"\nAvailable presets: {len(presets)}")
        for preset in presets:
            print(f"  • {preset}")
        
        # Load and display quick_test preset
        print("\nLoading 'quick_test' preset...")
        config = self.config_manager.load_preset("quick_test")
        
        print(f"\nConfiguration loaded:")
        print(f"  Name: {config.name}")
        print(f"  Description: {config.description}")
        print(f"  Algorithms: {len(config.algorithms.algorithms)}")
        print(f"  Heuristics: {len(config.heuristics.heuristics)}")
        print(f"  Stacks: {len(config.stacks.stacks)}")
        print(f"  Total experiments: {config.get_total_experiments()}")
        
        # Display configuration report
        report = self.config_manager.generate_config_report(config)
        print(f"\nConfiguration Report:\n{report}")
        
        return config
    
    def demo_custom_configuration(self):
        """Demonstrate creating and using custom configuration"""
        print("\n" + "="*80)
        print("DEMO 2: CUSTOM CONFIGURATION")
        print("="*80)
        
        from config.enums import AlgorithmType, HeuristicType, StackType
        from config.algorithm_config import AlgorithmConfig, AlgorithmSuiteConfig
        from config.heuristic_config import HeuristicConfig, HeuristicSuiteConfig
        from config.stack_config import StackGenerationConfig, StackSuiteConfig
        
        # Create custom configuration
        custom_config = ExperimentConfig(
            name="My Custom Analysis",
            description="Custom analysis focusing on aggressive play",
            
            algorithms=AlgorithmSuiteConfig(
                algorithms=[
                    AlgorithmConfig(
                        name="AlphaBeta-Aggressive",
                        algorithm_type=AlgorithmType.ALPHA_BETA,
                        description="Alpha-beta with aggressive settings",
                        depth_limit=6,
                        use_move_ordering=True
                    ),
                    AlgorithmConfig(
                        name="Minimax-Conservative",
                        algorithm_type=AlgorithmType.MINIMAX,
                        description="Minimax with conservative depth",
                        depth_limit=4
                    )
                ]
            ),
            
            heuristics=HeuristicSuiteConfig(
                heuristics=[
                    HeuristicConfig(
                        name="Aggressive-High",
                        heuristic_type=HeuristicType.AGGRESSIVE,
                        description="Highly aggressive play",
                        parameters={"bust_penalty": 20000}
                    ),
                    HeuristicConfig(
                        name="Closeness-Balanced",
                        heuristic_type=HeuristicType.CLOSENESS,
                        description="Balanced closeness focus"
                    )
                ]
            ),
            
            stacks=StackSuiteConfig(
                stacks=[
                    StackGenerationConfig(
                        stack_type=StackType.RANDOM,
                        length=8,
                        name="Random-8"
                    ),
                    StackGenerationConfig(
                        stack_type=StackType.BIASED_HIGH,
                        length=10,
                        name="Biased-High-10",
                        parameters={"bias_value": 6, "bias_strength": 0.8}
                    )
                ]
            )
        )
        
        print(f"\nCustom configuration created:")
        print(f"  Name: {custom_config.name}")
        print(f"  Algorithms: {len(custom_config.algorithms.algorithms)}")
        print(f"  Heuristics: {len(custom_config.heuristics.heuristics)}")
        print(f"  Stacks: {len(custom_config.stacks.stacks)}")
        print(f"  Total experiments: {custom_config.get_total_experiments()}")
        
        # Validate configuration
        errors = custom_config.validate()
        if errors:
            print(f"\nValidation errors:")
            for error in errors:
                print(f"  • {error}")
        else:
            print(f"\n✓ Configuration is valid!")
        
        # Save to file
        output_dir = Path("custom_configs")
        output_dir.mkdir(exist_ok=True)
        
        config_file = output_dir / "my_custom_config.json"
        custom_config.to_json(str(config_file))
        
        print(f"\nConfiguration saved to: {config_file}")
        
        return custom_config
    
    def demo_integration_with_full_analysis(self):
        """Demonstrate integration with existing full_analysis.py"""
        print("\n" + "="*80)
        print("DEMO 3: INTEGRATION WITH EXISTING FULL_ANALYSIS")
        print("="*80)
        
        # Load a configuration
        config = self.config_manager.load_preset("quick_test")
        
        # Create analyzer from full_analysis.py
        analyzer = FixedGameAnalyzer(log_level="INFO")
        
        print("\nRunning fixed game analysis with configured stacks...")
        
        # Use stacks from configuration
        for i, stack_config in enumerate(config.stacks.stacks[:2]):  # Just test first 2
            stack = stack_config.generate_stack()
            
            print(f"\nAnalyzing stack {i+1}: {stack_config.name}")
            print(f"  Stack: {stack}")
            print(f"  Type: {stack_config.stack_type.value}")
            print(f"  Length: {stack_config.length}")
            
            # Run analysis using existing code
            result = analyzer.analyze_game(stack, algorithm="both", depth_limit=5)
            
            # Store results
            self.results[f"stack_{i+1}"] = {
                "stack_config": stack_config.name,
                "stack": stack,
                "minimax_value": result.get("minimax", {}).get("value", 0),
                "alphabeta_value": result.get("alphabeta", {}).get("value", 0),
                "comparison": result.get("comparison", {})
            }
            
            # Display comparison
            if "comparison" in result:
                comp = result["comparison"]
                print(f"  Values match: {comp.get('values_match', False)}")
                print(f"  Speedup: {comp.get('speedup_factor', 0):.2f}x")
                print(f"  Pruning efficiency: {comp.get('pruning_efficiency', 0):.2%}")
        
        print("\n✓ Analysis complete using unified configuration!")
        
        return analyzer
    
    def demo_integration_with_heuristic_analysis(self):
        """Demonstrate integration with existing heuristic_analysis.py"""
        print("\n" + "="*80)
        print("DEMO 4: INTEGRATION WITH HEURISTIC_ANALYSIS")
        print("="*80)
        
        # Load heuristic analysis configuration
        config = self.config_manager.load_preset("heuristic_analysis")
        
        print("\nRunning heuristic analysis with configured stacks...")
        
        # Create heuristic analyzer
        analyzer = HeuristicAnalysis()
        analyzer.define_heuristic_families()
        
        # Use stacks from configuration
        analysis_results = {}
        
        for i, stack_config in enumerate(config.stacks.stacks[:3]):  # Just test first 3
            stack = stack_config.generate_stack()
            
            print(f"\nAnalyzing stack {i+1}: {stack_config.name}")
            print(f"  Stack: {stack}")
            
            # Run analysis on this stack
            stack_results = {}
            
            # Test each heuristic family
            for family_name, variations in analyzer.heuristic_families.items():
                family_results = analyzer.run_analysis(stack, family_name, variations)
                stack_results[family_name] = family_results
            
            analysis_results[stack_config.name] = stack_results
            
            # Generate quick comparison
            self._compare_heuristics(stack_results, stack_config.name)
        
        print("\n✓ Heuristic analysis complete using unified configuration!")
        
        return analysis_results
    
    def _compare_heuristics(self, stack_results, stack_name):
        """Quick comparison of heuristics for a stack"""
        print(f"\n  Quick comparison for {stack_name}:")
        
        for family_name, family_results in stack_results.items():
            best_variation = None
            best_total = 0
            
            for variation_name, results in family_results.items():
                final_total = results.get("final_total", 0)
                if final_total > best_total:
                    best_total = final_total
                    best_variation = variation_name
            
            if best_variation:
                distance = abs(21 - best_total)
                print(f"    {family_name}: {best_variation} → Total: {best_total} (Distance: {distance})")
    
    def demo_configuration_export_import(self):
        """Demonstrate configuration export and import"""
        print("\n" + "="*80)
        print("DEMO 5: CONFIGURATION EXPORT AND IMPORT")
        print("="*80)
        
        # Create a configuration
        from config.experiment_config import ExperimentConfig
        from config.algorithm_config import AlgorithmSuiteConfig
        from config.heuristic_config import HeuristicSuiteConfig
        from config.stack_config import StackSuiteConfig
        
        config = ExperimentConfig(
            name="Export Test",
            description="Test configuration export/import",
            algorithms=AlgorithmSuiteConfig.default_suite(),
            heuristics=HeuristicSuiteConfig.default_suite(),
            stacks=StackSuiteConfig.quick_suite()
        )
        
        # Export to JSON
        print("\nExporting configuration to JSON...")
        json_str = config.to_json()
        print(f"✓ Configuration serialized to JSON ({len(json_str)} characters)")
        
        # Save to file
        export_file = Path("exported_config.json")
        config.to_json(str(export_file))
        print(f"✓ Configuration saved to: {export_file}")
        
        # Import from file
        print("\nImporting configuration from file...")
        imported_config = ExperimentConfig.from_json(str(export_file))
        print(f"✓ Configuration imported: {imported_config.name}")
        
        # Verify
        print(f"\nVerification:")
        print(f"  Original name: {config.name}")
        print(f"  Imported name: {imported_config.name}")
        print(f"  Match: {config.name == imported_config.name}")
        
        print(f"  Original algorithms: {len(config.algorithms.algorithms)}")
        print(f"  Imported algorithms: {len(imported_config.algorithms.algorithms)}")
        print(f"  Match: {len(config.algorithms.algorithms) == len(imported_config.algorithms.algorithms)}")
        
        # Clean up
        export_file.unlink()
        print(f"\n✓ Cleaned up temporary file")
        
        return config, imported_config
    
    def run_all_demos(self):
        """Run all demonstration scenarios"""
        print("\n" + "="*80)
        print("UNIFIED CONFIGURATION MANAGEMENT - FULL DEMONSTRATION")
        print("="*80)
        
        demos = [
            ("Preset Loading", self.demo_preset_loading),
            ("Custom Configuration", self.demo_custom_configuration),
            ("Full Analysis Integration", self.demo_integration_with_full_analysis),
            ("Heuristic Analysis Integration", self.demo_integration_with_heuristic_analysis),
            ("Export/Import", self.demo_configuration_export_import)
        ]
        
        for demo_name, demo_func in demos:
            input(f"\nPress Enter to run {demo_name} demo...")
            demo_func()
        
        print("\n" + "="*80)
        print("ALL DEMONSTRATIONS COMPLETE!")
        print("="*80)
        
        self._generate_demo_summary()
    
    def _generate_demo_summary(self):
        """Generate summary of demo results"""
        print("\n" + "="*80)
        print("DEMONSTRATION SUMMARY")
        print("="*80)
        
        print("\nWhat was demonstrated:")
        print("  1. ✓ Loading preset configurations")
        print("  2. ✓ Creating custom configurations")
        print("  3. ✓ Integrating with existing analysis tools")
        print("  4. ✓ Exporting/importing configurations")
        print("  5. ✓ Validating configurations")
        print("  6. ✓ Generating configuration reports")
        
        print("\nConfiguration system is now fully integrated with:")
        print("  • FixedGameAnalyzer (full_analysis.py)")
        print("  • HeuristicAnalysis (heuristic_analysis.py)")
        print("  • SolutionPathDemo (solution_path_demo.py)")
        print("  • All existing algorithms (minimax, alpha-beta)")
        print("  • All existing heuristics (closeness, aggressive, cautious, balanced)")
        
        print("\nNext steps:")
        print("  1. Run: python experiment_runner.py --preset quick_test")
        print("  2. Run: python integrated_analysis.py --preset comprehensive_benchmark")
        print("  3. Create custom configs in custom_configs/ directory")


def main():
    """Main entry point for configuration integration demo"""
    try:
        demo = ConfigIntegrationDemo()
        demo.run_all_demos()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
