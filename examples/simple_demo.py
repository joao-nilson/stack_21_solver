# 
# simple_demo.py
#!/usr/bin/env python3
"""Simple demo of the configuration system"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("\n" + "="*80)
    print("CONFIGURATION SYSTEM DEMO")
    print("="*80)
    
    try:
        from config import ConfigManager, print_config_summary
        
        # Create configuration manager
        manager = ConfigManager()
        
        print("\n1. Available presets:")
        for i, preset in enumerate(manager.get_preset_names(), 1):
            print(f"   {i}. {preset}")
        
        # Load quick test preset
        print("\n2. Loading 'quick_test' preset...")
        config = manager.load_preset("quick_test")
        
        # Print summary
        print("\n3. Configuration Summary:")
        print_config_summary(config)
        
        # Get experiment combinations
        print("\n4. Generating experiment combinations...")
        combinations = config.get_experiment_combinations()
        print(f"   Total combinations: {len(combinations)}")
        
        if combinations:
            print("\n   Example combinations:")
            for i, combo in enumerate(combinations[:5], 1):
                print(f"   {i}. {combo['algorithm'].name} + "
                      f"{combo['heuristic'].name} + "
                      f"{combo['stack'].length} values")
        
        # Save configuration
        print("\n5. Saving configuration...")
        manager.save_config(config, "demo_config.json")
        print("   ✓ Saved to 'configs/demo_config.json'")
        
        # Load it back
        print("\n6. Loading saved configuration...")
        loaded_config = manager.load_config("demo_config.json")
        print("   ✓ Loaded successfully")
        
        # Clean up
        import os
        if os.path.exists("configs/demo_config.json"):
            os.remove("configs/demo_config.json")
            print("   ✓ Cleaned up test file")
        
        print("\n" + "="*80)
        print("DEMO COMPLETE! ✓")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80)
        print("DEMO FAILED ❌")
        print("="*80)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())