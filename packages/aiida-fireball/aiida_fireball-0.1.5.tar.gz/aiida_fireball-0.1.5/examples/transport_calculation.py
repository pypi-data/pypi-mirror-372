#!/usr/bin/env python3
"""
Transport calculation example.

This example demonstrates how to set up transport calculations
with all optional files (interaction, eta, trans, bias).
"""

from aiida import orm, engine
from aiida.plugins import CalculationFactory, DataFactory

def example_transport_calculation():
    """Run a transport calculation with all optional files."""
    
    # Load the Fireball calculation plugin
    FireballCalculation = CalculationFactory('fireball')
    StructureData = DataFactory('structure')
    
    # Create a carbon chain structure for transport
    structure = StructureData()
    # Set a cell suitable for transport calculations
    structure.set_cell([[20.0, 0.0, 0.0], 
                       [0.0, 15.0, 0.0], 
                       [0.0, 0.0, 15.0]])
    
    # Create a simple carbon chain
    for i in range(5):
        structure.append_atom(position=[i * 1.4, 0.0, 0.0], symbols='C')
    
    # Get the code
    try:
        code = orm.load_code('fireball@localhost')
    except:
        print("Error: Code 'fireball@localhost' not found.")
        print("Please set up your Fireball code first.")
        return
    
    # Set up kpoints
    from aiida.plugins import DataFactory
    KpointsData = DataFactory('kpoints')
    kpoints = KpointsData()
    kpoints.set_kpoints_mesh([1, 1, 1])  # Gamma point for transport
    
    # Get Fdata remote folder
    try:
        fdata_remote = orm.load_node('fdata_remote_pk')  # Replace with actual PK
    except:
        print("Error: fdata_remote not found. You need to set up Fdata files first.")
        return
    
    # Define basic Fireball parameters
    basic_parameters = {
        'OPTION': {
            'iimage': 1,  # basic single point calculation
        },
        'OUTPUT': {
            'iwrtpop': 1,
        }
    }
    
    # Define transport settings (these go in settings, not parameters)
    transport_settings = {
        'TRANSPORT': {
            'INTERACTION': {
                'ncell1': 0,
                'total_atoms1': 5,
                'ninterval1': 1,
                'intervals1': [[1, 5]],
                'natoms_tip1': 2,
                'atoms1': [1, 2],
                'ncell2': 0,
                'total_atoms2': 5,
                'ninterval2': 1,
                'intervals2': [[4, 5]],
                'natoms_tip2': 2,
                'atoms2': [4, 5]
            },
            'ETA': {
                'imag_part': 0.01,
                'intervals': [[1, 2], [4, 5]]
            },
            'TRANS': {
                'ieta': True,
                'iwrt_trans': True,
                'ichannel': False,
                'ifithop': 1,
                'Ebottom': -2.0,
                'Etop': 2.0,
                'nsteps': 100,
                'eta': 0.01
            },
            'BIAS': {
                'bias': 1.0,
                'z_top': 10.0,
                'z_bottom': 0.0
            }
        }
    }
    
    # Prepare inputs
    inputs = {
        'code': code,
        'structure': structure,
        'parameters': orm.Dict(dict=basic_parameters),
        'kpoints': kpoints,
        'fdata_remote': fdata_remote,
        'settings': orm.Dict(dict=transport_settings),
        'metadata': {
            'label': 'carbon_chain_transport',
            'description': 'Transport calculation for carbon chain with all optional files',
            'options': {
                'resources': {'num_machines': 1},
                'max_wallclock_seconds': 3600,  # 1 hour
            }
        }
    }
    
    # Submit the calculation
    calc_node = engine.submit(FireballCalculation, **inputs)
    print(f"Submitted transport calculation with PK={calc_node.pk}")
    print(f"This calculation will generate all optional files:")
    print("  - interaction.optional")
    print("  - eta.optional") 
    print("  - trans.optional")
    print("  - bias.optional")
    print(f"Monitor with: verdi process status {calc_node.pk}")
    
    return calc_node

if __name__ == '__main__':
    print("Running transport calculation example...")
    example_transport_calculation()
