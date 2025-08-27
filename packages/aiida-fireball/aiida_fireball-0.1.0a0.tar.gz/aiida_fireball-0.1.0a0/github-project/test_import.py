#!/usr/bin/env python3
"""
Test basic import to ensure plugin loads correctly.
"""

def test_plugin_import():
    """Test that the plugin can be imported without errors."""
    try:
        from aiida_fireball import __version__
        from aiida_fireball.calculations.fireball import FireballCalculation
        print(f"Plugin version: {__version__}")
        print("Basic import test passed!")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

if __name__ == "__main__":
    success = test_plugin_import()
    exit(0 if success else 1)
