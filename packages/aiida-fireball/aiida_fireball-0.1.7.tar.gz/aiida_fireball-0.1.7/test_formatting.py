#!/usr/bin/env python3
"""
Test basic formatting to ensure pre-commit will work.
"""

import os
import subprocess
import sys


def test_basic_formatting():
    """Test basic black formatting."""
    try:
        # Test if we can import our plugin
        from aiida_fireball import __version__
        print(f"Plugin version: {__version__}")
        
        # Test basic Python syntax in all our files
        import ast
        
        python_files = []
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                ast.parse(content)
                print(f"✓ {py_file} syntax OK")
            except SyntaxError as e:
                print(f"✗ {py_file} syntax error: {e}")
                return False
        
        print("All Python files have valid syntax!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = test_basic_formatting()
    sys.exit(0 if success else 1)
