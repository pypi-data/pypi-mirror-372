# Getting Started with AiiDA Fireball

AiiDA Fireball is a plugin for running Fireball calculations within the AiiDA framework. This tutorial will guide you through setting up and running your first calculation.

![Fireball Structure](../_static/fireball_structure.png)

## Prerequisites

Before starting, ensure you have:
- AiiDA installed and configured
- Fireball code installed on your computer
- Fireball Fdata files available

## Quick Start Tutorial

### Step 1: Set Up AiiDA Computer and Code

First, configure your computer and Fireball code in AiiDA:

```bash
# Set up computer (if not already done)
verdi computer setup -L localhost -H localhost -T core.local -S core.direct -w /tmp

# Set up Fireball code
verdi code create core.code.installed -L fireball@localhost --computer localhost --filepath-executable /path/to/fireball.x --default-calc-job-plugin fireball
```

### Step 2: Prepare Fdata Files

Upload your Fireball Fdata files to AiiDA:

```python
from aiida import orm
from aiida.plugins import DataFactory

# Create a folder data node for Fdata files
FolderData = DataFactory('core.folder')
fdata_folder = FolderData()

# Add your Fdata files to the folder
import tempfile
import os

with tempfile.TemporaryDirectory() as tmpdir:
    # Copy your Fdata files to this temporary directory
    # For example: cp -r /path/to/your/Fdata/* tmpdir/
    fdata_folder.put_object_from_tree(tmpdir)

fdata_folder.store()
print(f"Fdata folder stored with PK: {fdata_folder.pk}")

# Create a remote data node pointing to Fdata location
RemoteData = DataFactory('core.remote')
fdata_remote = RemoteData(remote_path='/path/to/Fdata', computer=computer)
fdata_remote.store()
```

### Step 3: Create a Simple Structure

Let's create a simple silicon crystal structure using ASE:

```python
from ase import Atoms
from ase.build import bulk
from aiida.plugins import DataFactory

StructureData = DataFactory('core.structure')

# Create a silicon crystal using ASE
si_ase = bulk('Si', 'diamond', a=5.43)

# Convert to AiiDA structure
structure = StructureData(ase=si_ase)
structure.store()
print(f"Silicon structure created: PK={structure.pk}")
```

### Step 4: Set Up Calculation Parameters

Define the Fireball calculation parameters:

```python
from aiida import orm

# Basic calculation parameters for silicon
parameters = {
    'OPTION': {
        'iimage': 1,        # Single point calculation
        'iquench': 0,       # No geometry optimization
        'dt': 0.25,         # Time step
        'nstepf': 1,        # Number of MD steps
    },
    'OUTPUT': {
        'iwrtdos': 0,       # Don't write DOS
        'iwrtxyz': 1,       # Write position trajectory
    }
}

parameters_node = orm.Dict(parameters)
parameters_node.store()
```

### Step 5: Set Up K-points

Define the k-point mesh for the calculation:

```python
from aiida.plugins import DataFactory

KpointsData = DataFactory('core.array.kpoints')

kpoints = KpointsData()
# Use a reasonable k-point mesh for silicon
kpoints.set_kpoints_mesh([4, 4, 4], offset=[0.0, 0.0, 0.0])
kpoints.store()
```

### Step 6: Run the Calculation

Submit the calculation:

```python
from aiida.plugins import CalculationFactory
from aiida.engine import submit

# Load the calculation plugin
FireballCalculation = CalculationFactory('fireball')

# Load your code
code = orm.load_code('fireball@localhost')  # Use your code label

# Alternative method using builder (recommended)
builder = FireballCalculation.get_builder()
builder.code = code
builder.structure = structure
builder.parameters = parameters_node
builder.kpoints = kpoints
builder.fdata_remote = fdata_remote
builder.metadata.label = 'silicon_scf'
builder.metadata.description = 'Silicon SCF calculation with Fireball'
builder.metadata.options.resources = {
    'num_machines': 1,
    'num_mpiprocs_per_machine': 1,
}
builder.metadata.options.max_wallclock_seconds = 1800  # 30 minutes

# Submit using builder
calc_node = submit(builder)

# Alternative: Set up all inputs as dictionary
inputs = {
    'code': code,
    'structure': structure,
    'parameters': parameters_node,
    'kpoints': kpoints,
    'fdata_remote': fdata_remote,
    'metadata': {
        'label': 'silicon_scf',
        'description': 'Silicon SCF calculation with Fireball',
        'options': {
            'resources': {
                'num_machines': 1,
                'num_mpiprocs_per_machine': 1,
            },
            'max_wallclock_seconds': 1800,  # 30 minutes
        }
    }
}

# Submit the calculation
# calc_node = submit(FireballCalculation, **inputs)

print(f"Submitted calculation with PK={calc_node.pk}")
print(f"Monitor with: verdi process status {calc_node.pk}")
```

### Step 7: Monitor the Calculation

Check the status of your calculation:

```bash
# Check calculation status
verdi process status <PK>

# View the calculation log
verdi process report <PK>

# List all processes
verdi process list
```

### Step 8: Analyze Results

Once the calculation finishes successfully:

```python
# Load the calculation node
calc = orm.load_node(<calc_pk>)

# Check if calculation completed successfully
if calc.is_finished_ok:
    print("Calculation completed successfully!")
    
    # Access output parameters
    if 'output_parameters' in calc.outputs:
        results = calc.outputs.output_parameters.get_dict()
        print("Key results:")
        print(f"  Total energy: {results.get('total_energy', 'N/A')} eV")
        print(f"  Calculation completed: {results.get('calculation_completed', False)}")
    
    # Access retrieved files
    if 'retrieved' in calc.outputs:
        retrieved = calc.outputs.retrieved
        files = retrieved.list_object_names()
        print(f"Retrieved files: {files}")
        
    # For geometry optimizations, check final structure from answer.bas
    if 'output_structure' in calc.outputs:
        final_structure = calc.outputs.output_structure
        print(f"Optimized structure available with {len(final_structure.sites)} atoms")
        
else:
    print(f"Calculation failed with state: {calc.process_state}")
    if calc.exit_message:
        print(f"Exit message: {calc.exit_message}")
```

## Understanding Fireball Output

### Key Output Files

- **aiida.out**: Main output file with calculation results
- **answer.bas**: Final atomic positions (for optimizations)
- **CHARGES**: Atomic charges

### Common Output Parameters

The `output_parameters` node contains important results:

- `total_energy`: Total energy of the system (eV)
- `calculation_completed`: Whether calculation finished normally
- `fermi_energy`: Fermi level (eV)

## Next Steps

- Learn about [advanced parallel calculations](advanced_parallel.md)
- Explore [transport calculations](transport_tutorial.md)
- Check out more [examples](https://github.com/mohamedmamlouk/aiida-fireball/tree/main/examples)

## Troubleshooting

### Common Issues

1. **Fdata files not found**: Ensure your `fdata_remote` points to the correct location
2. **Code not found**: Check that your Fireball code is properly configured with `verdi code list`
3. **Out of memory**: Adjust your k-point mesh or calculation parameters

### Getting Help

- Check the [Fireball documentation](https://fireball-qmd.github.io/fireball.html)
- Visit the [AiiDA documentation](https://aiida.readthedocs.io/)
- Report issues on [GitHub](https://github.com/mohamedmamlouk/aiida-fireball/issues)
