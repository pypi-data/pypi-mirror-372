#!/usr/bin/env python3
"""
basic_calculation.py

Simple water molecule single-point calculation example.
"""

import aiida
aiida.load_profile()

from aiida.orm import load_code, Dict, RemoteData, KpointsData, StructureData
from aiida.engine import submit
from aiida_fireball.calculations.fireball import FireballCalculation

# Create water molecule structure
structure = StructureData()
structure.set_cell([
    [10.0, 0.0, 0.0],
    [0.0, 10.0, 0.0], 
    [0.0, 0.0, 10.0]
])

# Add atoms (positions in Angstroms)
structure.append_atom(position=[0.0, 0.0, 0.0], symbols='O')
structure.append_atom(position=[0.757, 0.587, 0.0], symbols='H')
structure.append_atom(position=[-0.757, 0.587, 0.0], symbols='H')

# Set up calculation
code = load_code('fireball@localhost')
fdata_remote = RemoteData(
    computer=code.computer,
    remote_path='/path/to/your/fdata'
)

# K-points (gamma point for molecules)
kpoints = KpointsData()
kpoints.set_kpoints_mesh([1, 1, 1])

# Basic parameters
parameters = Dict(dict={
    'OPTION': {
        'iimage': 1,        # Single point calculation
        'iquench': 0,       # No optimization
        'dt': 0.5,          # Time step
        'nstepf': 1,        # Number of steps
    },
    'OUTPUT': {
        'iwrtpop': 1,       # Write population analysis
        'iwrtdos': 0,       # Don't write DOS
        'iwrtatom': 1,      # Write atomic information
    }
})

# Submit calculation
builder = FireballCalculation.get_builder()
builder.code = code
builder.structure = structure
builder.kpoints = kpoints
builder.parameters = parameters
builder.fdata_remote = fdata_remote

builder.metadata.label = 'water_molecule'
builder.metadata.options.resources = {'num_machines': 1}
builder.metadata.options.max_wallclock_seconds = 600

calc_node = submit(builder)
print(f"Submitted water molecule calculation: PK={calc_node.pk}")
