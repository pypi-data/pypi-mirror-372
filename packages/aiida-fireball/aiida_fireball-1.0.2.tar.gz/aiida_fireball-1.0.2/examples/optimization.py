#!/usr/bin/env python3
"""
Structure optimization example.

This example shows how to set up and run a geometry optimization
calculation using the AiiDA Fireball plugin.
"""

from aiida import orm, engine
from aiida.plugins import CalculationFactory, DataFactory

def example_optimization():
    """Run a geometry optimization calculation."""
    
    # Load the Fireball calculation plugin
    FireballCalculation = CalculationFactory('fireball')
    StructureData = DataFactory('structure')
    
    # Create a simple H2O molecule structure (initial guess)
    structure = StructureData()
    # Set a cubic cell with 12 Å sides
    structure.set_cell([[12.0, 0.0, 0.0], 
                       [0.0, 12.0, 0.0], 
                       [0.0, 0.0, 12.0]])
    
    # Add H2O atoms with approximate positions
    structure.append_atom(position=[0.0, 0.0, 0.0], symbols='O')     # Oxygen
    structure.append_atom(position=[0.96, 0.0, 0.0], symbols='H')    # Hydrogen 1
    structure.append_atom(position=[-0.24, 0.93, 0.0], symbols='H')  # Hydrogen 2
    
    # Get the code
    try:
        code = orm.load_code('fireball@localhost')
    except:
        print("Error: Code 'fireball@localhost' not found.")
        print("Please set up your Fireball code first using:")
        print("verdi code setup")
        return
    
    # Define optimization parameters (using Fireball namelists)
    optimization_parameters = {
        'OPTION': {
            'iimage': 2,  # molecular dynamics with optimization
            'iquench': 1,  # quench (optimize) the forces
            'dt': 0.5,     # time step in fs
            'nstepf': 100, # maximum number of steps
        },
        'OUTPUT': {
            'iwrtxyz': 1,  # write forces
            
        }
    }
    
    # Add kpoints for the calculation
    from aiida.plugins import DataFactory
    KpointsData = DataFactory('kpoints')
    kpoints = KpointsData()
    kpoints.set_kpoints_mesh([1, 1, 1])  # Gamma point only for molecules
    
    # Get or create Fdata remote folder (you need to set this up)
    try:
        # Try to load existing Fdata remote folder
        fdata_remote = orm.load_node('fdata_remote_pk')  # Replace with actual PK
    except:
        print("Error: fdata_remote not found. You need to set up Fdata files first.")
        print("Please upload Fdata directory and create a RemoteData node.")
        return
    
    # Prepare inputs
    inputs = {
        'code': code,
        'structure': structure,
        'parameters': orm.Dict(dict=optimization_parameters),
        'kpoints': kpoints,
        'fdata_remote': fdata_remote,
        'metadata': {
            'label': 'H2O_optimization',
            'description': 'Geometry optimization of H2O molecule',
            'options': {
                'resources': {'num_machines': 1},
                'max_wallclock_seconds': 2400,  # 40 minutes
            }
        }
    }
    
    # Submit the calculation
    calc_node = engine.submit(FireballCalculation, **inputs)
    print(f"Submitted optimization calculation with PK={calc_node.pk}")
    print(f"This calculation will optimize the H2O geometry")
    print(f"Monitor with: verdi process status {calc_node.pk}")
    
    return calc_node

def analyze_optimization_results(calc_pk):
    """Analyze the results of a completed optimization calculation."""
    
    try:
        calc_node = orm.load_node(calc_pk)
    except:
        print(f"Error: Cannot load calculation with PK={calc_pk}")
        return
    
    if not calc_node.is_finished_ok:
        print(f"Calculation {calc_pk} is not finished successfully.")
        print(f"Status: {calc_node.process_state}")
        return
    
    # Check if optimization completed successfully
    if 'output_parameters' in calc_node.outputs:
        output_params = calc_node.outputs.output_parameters.get_dict()
        print(f"Optimization results for calculation {calc_pk}:")
        
        # Check if we have trajectory data for optimization steps
        if 'output_trajectory' in calc_node.outputs:
            trajectory = calc_node.outputs.output_trajectory
            print(f"  Optimization trajectory PK: {trajectory.pk}")
            print(f"  Number of optimization steps: {trajectory.numsteps}")
            
            # Get final energy if available
            if 'total_energy' in output_params:
                print(f"  Final total energy: {output_params['total_energy']:.6f} eV")
            
            # Get final forces if available
            if 'forces' in output_params:
                print(f"  Final max force: {max(abs(f) for f in output_params['forces']):.6f} eV/Å")
        
        # Get the final structure if available
        if 'output_structure' in calc_node.outputs:
            optimized_structure = calc_node.outputs.output_structure
            print(f"  Final structure PK: {optimized_structure.pk}")
            
            # Compare initial and final positions
            initial_structure = calc_node.inputs.structure
            initial_positions = initial_structure.get_positions()
            final_positions = optimized_structure.get_positions()
            
            print("\n  Atomic positions (Å):")
            symbols = initial_structure.get_symbols()
            for i, symbol in enumerate(symbols):
                print(f"    {symbol} {i+1}:")
                print(f"      Initial:  ({initial_positions[i][0]:.3f}, {initial_positions[i][1]:.3f}, {initial_positions[i][2]:.3f})")
                print(f"      Final:    ({final_positions[i][0]:.3f}, {final_positions[i][1]:.3f}, {final_positions[i][2]:.3f})")
                
                # Calculate displacement
                displacement = ((final_positions[i] - initial_positions[i])**2).sum()**0.5
                print(f"      Displacement: {displacement:.3f} Å")
        
    else:
        print("No output parameters found - check if calculation completed successfully.")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'analyze':
        if len(sys.argv) > 2:
            calc_pk = int(sys.argv[2])
            analyze_optimization_results(calc_pk)
        else:
            print("Usage: python optimization.py analyze <calc_pk>")
    else:
        print("Running structure optimization example...")
        calc = example_optimization()
        print(f"\nTo analyze results when finished, run:")
        print(f"python optimization.py analyze {calc.pk}")
