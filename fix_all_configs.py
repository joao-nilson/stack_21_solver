# fix_all_configs.py
#!/usr/bin/env python3
"""Comprehensive fix for all configuration issues"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def fix_and_test():
    """Fix and test all configuration components"""
    print("\n" + "="*80)
    print("COMPREHENSIVE CONFIGURATION FIX")
    print("="*80)
    
    # First, let's test basic imports and class creation
    print("\n1. Testing basic imports and class creation...")
    
    try:
        from config.enums import AlgorithmType, HeuristicType, StackType
        from config.algorithm_config import AlgorithmConfig
        from config.heuristic_config import HeuristicConfig
        from config.stack_config import StackGenerationConfig
        
        print("✓ All imports successful")
        
        # Test creating each class
        algo = AlgorithmConfig(
            name="Test-Algo",
            algorithm_type=AlgorithmType.MINIMAX
        )
        print(f"✓ Created AlgorithmConfig: {algo.name}")
        
        heuristic = HeuristicConfig(
            name="Test-Heuristic", 
            heuristic_type=HeuristicType.CLOSENESS
        )
        print(f"✓ Created HeuristicConfig: {heuristic.name}")
        
        stack = StackGenerationConfig(
            stack_type=StackType.RANDOM,
            length=6,
            name="Test-Stack"
        )
        print(f"✓ Created StackGenerationConfig: {stack.name}")
        
        print("\n✓ Basic class creation tests passed!")
        
    except Exception as e:
        print(f"✗ Basic tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test ConfigManager and presets
    print("\n2. Testing ConfigManager and presets...")
    
    try:
        from config.config_manager import ConfigManager
        
        manager = ConfigManager()
        presets = manager.get_preset_names()
        print(f"Available presets: {', '.join(presets)}")
        
        successful_presets = []
        failed_presets = []
        
        for preset_name in presets:
            print(f"\n  Testing preset: {preset_name}")
            try:
                config = manager.load_preset(preset_name)
                print(f"    ✓ Loaded: {config.name}")
                
                # Check that all components are proper objects
                print(f"    Algorithms: {len(config.algorithms.algorithms)}")
                for algo in config.algorithms.algorithms:
                    if not isinstance(algo, AlgorithmConfig):
                        raise TypeError(f"Algorithm is {type(algo)}, not AlgorithmConfig")
                
                print(f"    Heuristics: {len(config.heuristics.heuristics)}")
                for heuristic in config.heuristics.heuristics:
                    if not isinstance(heuristic, HeuristicConfig):
                        raise TypeError(f"Heuristic is {type(heuristic)}, not HeuristicConfig")
                
                print(f"    Stacks: {len(config.stacks.stacks)}")
                for stack in config.stacks.stacks:
                    if not isinstance(stack, StackGenerationConfig):
                        raise TypeError(f"Stack is {type(stack)}, not StackGenerationConfig")
                
                # Validate
                errors = config.validate()
                if errors:
                    print(f"    ⚠ Validation errors: {len(errors)}")
                    for error in errors[:2]:
                        print(f"      - {error}")
                else:
                    print(f"    ✓ Validation passed")
                
                successful_presets.append(preset_name)
                
            except Exception as e:
                print(f"    ✗ Failed: {e}")
                failed_presets.append(preset_name)
        
        print(f"\n✓ Preset loading: {len(successful_presets)}/{len(presets)} successful")
        
        if failed_presets:
            print(f"  Failed presets: {', '.join(failed_presets)}")
            return False
        
    except Exception as e:
        print(f"✗ ConfigManager tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test serialization/deserialization
    print("\n3. Testing serialization/deserialization...")
    
    try:
        from config.config_manager import ConfigManager
        
        manager = ConfigManager()
        config = manager.load_preset("algorithm_comparison")
        
        # Save to JSON
        import json
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_str = config.to_json(f.name)
            temp_path = f.name
        
        print(f"✓ Saved config to temporary file")
        
        # Load from JSON
        from config.experiment_config import ExperimentConfig
        loaded_config = ExperimentConfig.from_json(temp_path)
        
        print(f"✓ Loaded config from JSON")
        
        # Compare
        if config.name == loaded_config.name:
            print(f"✓ Config names match: {config.name}")
        else:
            print(f"✗ Config names don't match: {config.name} vs {loaded_config.name}")
        
        # Clean up
        os.unlink(temp_path)
        print(f"✓ Cleaned up temporary file")
        
    except Exception as e:
        print(f"✗ Serialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def create_working_example():
    """Create a working example configuration"""
    print("\n4. Creating a working example...")
    
    try:
        from config.enums import AlgorithmType, HeuristicType, StackType
        from config.algorithm_config import AlgorithmConfig, AlgorithmSuiteConfig
        from config.heuristic_config import HeuristicConfig, HeuristicSuiteConfig
        from config.stack_config import StackGenerationConfig, StackSuiteConfig
        from config.experiment_config import ExperimentConfig, ExperimentConstraints
        
        # Create a simple working configuration
        config = ExperimentConfig(
            name="Working Example",
            description="A simple working example configuration",
            algorithms=AlgorithmSuiteConfig(
                algorithms=[
                    AlgorithmConfig(
                        name="Simple-Minimax",
                        algorithm_type=AlgorithmType.MINIMAX,
                        depth_limit=3
                    )
                ]
            ),
            heuristics=HeuristicSuiteConfig(
                heuristics=[
                    HeuristicConfig(
                        name="Simple-Heuristic",
                        heuristic_type=HeuristicType.CLOSENESS
                    )
                ]
            ),
            stacks=StackSuiteConfig(
                stacks=[
                    StackGenerationConfig(
                        stack_type=StackType.RANDOM,
                        length=6,
                        name="Simple-Stack"
                    )
                ]
            ),
            constraints=ExperimentConstraints(
                max_total_time_seconds=60
            )
        )
        
        print(f"✓ Created working example: {config.name}")
        
        # Validate
        errors = config.validate()
        if errors:
            print(f"⚠ Validation errors: {len(errors)}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"✓ Configuration is valid")
        
        # Get experiment combinations
        combinations = config.get_experiment_combinations()
        print(f"✓ Generated {len(combinations)} experiment combinations")
        
        if combinations:
            print(f"\n  Example combination:")
            combo = combinations[0]
            print(f"    Algorithm: {combo['algorithm'].name}")
            print(f"    Heuristic: {combo['heuristic'].name}")
            print(f"    Stack: {combo['stack'].name} ({combo['stack'].length} values)")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create working example: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    
    print("\nStarting comprehensive configuration fix...")
    
    # Run tests
    test1 = fix_and_test()
    test2 = create_working_example()
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    if test1 and test2:
        print("✓ ALL TESTS PASSED! 🎉")
        print("\nThe configuration system is now working correctly.")
        print("\nNext steps:")
        print("1. Run the unified analyzer to test with real algorithms")
        print("2. Create custom configurations for your specific experiments")
        print("3. Extend with custom algorithms, heuristics, or stack types")
    else:
        print("✗ SOME TESTS FAILED ❌")
        print("\nIssues found:")
        if not test1:
            print("  - Basic configuration tests failed")
        if not test2:
            print("  - Could not create working example")
        print("\nPlease check the error messages above for details.")
    
    print("="*80)
    
    return test1 and test2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)