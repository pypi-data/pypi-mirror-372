#!/usr/bin/env python3
"""
Helper script to set up Fdata remote folder for AiiDA Fireball calculations.

This script helps you upload and register Fdata files needed for Fireball calculations.
"""

import os
import sys
from pathlib import Path
from aiida import orm

def setup_fdata_remote(computer_label='localhost', fdata_path=None):
    """Set up Fdata remote folder on the specified computer."""
    
    if fdata_path is None:
        print("Please provide the path to your Fdata directory.")
        print("Usage: python setup_fdata.py /path/to/Fdata")
        return None
    
    fdata_path = Path(fdata_path)
    if not fdata_path.exists():
        print(f"Error: Fdata directory not found at {fdata_path}")
        return None
    
    # Check if Fdata directory contains required files
    required_files = ['Fdata.inp']  # Add other required files as needed
    missing_files = []
    for req_file in required_files:
        if not (fdata_path / req_file).exists():
            missing_files.append(req_file)
    
    if missing_files:
        print(f"Warning: Missing required files in Fdata directory: {missing_files}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return None
    
    try:
        # Load the computer
        computer = orm.load_computer(computer_label)
        print(f"Using computer: {computer.label}")
    except:
        print(f"Error: Computer '{computer_label}' not found.")
        print("Available computers:")
        for comp in orm.QueryBuilder().append(orm.Computer).all(flat=True):
            print(f"  - {comp.label}")
        return None
    
    # Create RemoteData node for Fdata
    fdata_remote = orm.RemoteData(
        computer=computer,
        remote_path=str(fdata_path.absolute())
    )
    fdata_remote.label = 'fdata_fireball'
    fdata_remote.description = f'Fdata directory for Fireball calculations from {fdata_path}'
    fdata_remote.store()
    
    print(f"✓ Fdata remote folder created with PK={fdata_remote.pk}")
    print(f"  Path: {fdata_remote.get_remote_path()}")
    print(f"  Computer: {fdata_remote.computer.label}")
    print(f"\nTo use in your calculations, replace 'fdata_remote_pk' with {fdata_remote.pk}")
    print(f"Or load with: fdata_remote = orm.load_node({fdata_remote.pk})")
    
    return fdata_remote

def list_fdata_nodes():
    """List all existing Fdata RemoteData nodes."""
    
    query = orm.QueryBuilder()
    query.append(orm.RemoteData, filters={'label': {'like': '%fdata%'}})
    
    fdata_nodes = query.all(flat=True)
    
    if not fdata_nodes:
        print("No Fdata remote folders found.")
        return
    
    print("Existing Fdata remote folders:")
    for node in fdata_nodes:
        print(f"  PK={node.pk}: {node.label}")
        print(f"    Path: {node.get_remote_path()}")
        print(f"    Computer: {node.computer.label}")
        print(f"    Description: {node.description}")
        print()

def main():
    """Main function."""
    
    if len(sys.argv) < 2:
        print("AiiDA Fireball Fdata Setup Helper")
        print("=" * 40)
        print("Usage:")
        print("  python setup_fdata.py <fdata_path>        # Setup new Fdata remote")
        print("  python setup_fdata.py list                # List existing Fdata remotes")
        print()
        print("Examples:")
        print("  python setup_fdata.py /home/user/Fdata")
        print("  python setup_fdata.py list")
        return
    
    if sys.argv[1] == 'list':
        list_fdata_nodes()
    else:
        fdata_path = sys.argv[1]
        computer_label = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        setup_fdata_remote(computer_label, fdata_path)

if __name__ == '__main__':
    main()
