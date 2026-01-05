#examples/config_demo.py
#!/usr/bin/env python3

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    ConfigManager,
    create_quick_test_config,
    create_comprehensive_config,
    print_config_summary
)


def demonstrate_config_management():
    """Demonstrate configuration management features"""
    
    print("\n" + "="*80)
    print("UNIFIED CONFIGURATION MANAGEMENT DEMO")
    print("="*80)
    
    # Create configuration manager
    config_manager = ConfigManager()
    
    print("\n1. Available Presets:")
    for preset_name in config_manager.get_preset_names():
        print(f"   - {preset_name}")
    
    print("\n2. Loading Quick Test Preset:")
    quick_config = config_manager.load_preset("quick_test")
    print_config_summary(quick_config)
    
    print("\n3. Loading Comprehensive Benchmark Preset:")
    comp_config = config_manager.load_preset("comprehensive_benchmark")
    print_config_summary(comp_config)
    
    print("\n4. Creating Custom Configuration:")
    custom_config = config_manager.create_custom_config(
        name="My Custom Experiment",
        description="Testing custom algorithm parameters",
        random_seed=12345,
        constraints={
            "max_total_time_seconds": 300,
            "max_parallel_workers": 2
        }
    )
    
    # Add a custom algorithm
    from config import AlgorithmConfig, AlgorithmType
    custom_algo = AlgorithmConfig(
        algorithm_type=AlgorithmType.ALPHA_BETA,
        name="My-AlphaBeta",
        description="Custom Alpha-Beta with special parameters",
        parameters={
            "use_killer_moves": True,
            "history_heuristic_depth": 3,
            "aspiration_window_size": 50
        },
        depth_limit=6
    )
    custom_config.algorithms.add_algorithm(custom_algo)
    
    print_config_summary(custom_config)
    
    print("\n5. Saving and Loading Configuration:")
    config_manager.save_config(custom_config, "my_custom_config.json")
    print("   Configuration saved to: configs/my_custom_config.json")
    
    loaded_config = config_manager.load_config("my_custom_config.json")
    print("   Configuration loaded successfully")
    
    print("\n6. Generating Experiment Combinations:")
    combinations = loaded_config.get_experiment_combinations()
    print(f"   Total combinations: {len(combinations)}")
    
    if combinations:
        print("\n   First 3 combinations:")
        for i, combo in enumerate(combinations[:3], 1):
            print(f"   {i}. {combo['combination_id']}")
    
    print("\n" + "="*80)
    print("CONFIGURATION DEMO COMPLETE")
    print("="*80)


def interactive_config_creator():
    """Interactive configuration creation"""
    print("\n" + "="*80)
    print("INTERACTIVE CONFIGURATION CREATOR")
    print("="*80)
    
    config_manager = ConfigManager()
    
    while True:
        print("\nOptions:")
        print("1. Create from preset")
        print("2. Create custom configuration")
        print("3. Load existing configuration")
        print("4. Validate configuration")
        print("5. Save configuration")
        print("6. Generate experiment combinations")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            print("\nAvailable presets:")
            for i, preset in enumerate(config_manager.get_preset_names(), 1):
                print(f"{i}. {preset}")
            
            preset_choice = input("\nSelect preset (number or name): ").strip()
            
            try:
                if preset_choice.isdigit():
                    preset_name = config_manager.get_preset_names()[int(preset_choice) - 1]
                else:
                    preset_name = preset_choice
                
                config = config_manager.load_preset(preset_name)
                print(f"\nLoaded preset: {preset_name}")
                print_config_summary(config)
                
            except (ValueError, IndexError) as e:
                print(f"Error: {e}")
        
        elif choice == "2":
            print("\nCustom configuration creation not yet implemented.")
            print("Use the programmatic API for now.")
        
        elif choice == "3":
            filename = input("\nEnter configuration filename: ").strip()
            try:
                config = config_manager.load_config(filename)
                print(f"\nConfiguration loaded from: {filename}")
                print_config_summary(config)
            except Exception as e:
                print(f"Error loading configuration: {e}")
        
        elif choice == "4":
            if 'config' not in locals():
                print("\nNo configuration loaded. Load one first.")
                continue
            
            validation = config_manager.validate_config(config)
            if validation['is_valid']:
                print("\nConfiguration is VALID")
            else:
                print("\nConfiguration is INVALID")
                print("Errors:")
                for error in validation['errors']:
                    print(f"  - {error}")
        
        elif choice == "5":
            if 'config' not in locals():
                print("\nNo configuration loaded. Load one first.")
                continue
            
            filename = input("\nEnter filename to save (default: my_config.json): ").strip()
            if not filename:
                filename = "my_config.json"
            
            config_manager.save_config(config, filename)
            print(f"\nConfiguration saved to: {filename}")
        
        elif choice == "6":
            if 'config' not in locals():
                print("\nNo configuration loaded. Load one first.")
                continue
            
            combinations = config.get_experiment_combinations()
            print(f"\nTotal experiment combinations: {len(combinations)}")
            
            if input("\nShow first 10 combinations? (y/n): ").lower() == 'y':
                for i, combo in enumerate(combinations[:10], 1):
                    print(f"{i:3}. {combo['combination_id']}")
        
        elif choice == "7":
            print("\nExiting...")
            break
        
        else:
            print("\nInvalid choice. Please enter 1-7.")


if __name__ == "__main__":
    demonstrate_config_management()
    
    if input("\nRun interactive configuration creator? (y/n): ").lower() == 'y':
        interactive_config_creator()
