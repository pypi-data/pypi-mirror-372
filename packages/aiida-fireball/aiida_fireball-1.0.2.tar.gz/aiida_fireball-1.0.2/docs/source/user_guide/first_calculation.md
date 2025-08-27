# Your First Calculation

This guide will walk you through setting up and running your first calculation with the AiiDA Fireball plugin.

## Prerequisites

Before starting, make sure you have:

- ✅ AiiDA installed and configured (`verdi status` should show all services running)
- ✅ AiiDA Fireball plugin installed (`pip install aiida-fireball`)
- ✅ Fireball code available and executable
- ✅ Basic understanding of AiiDA concepts (nodes, processes, workflows)

## Step 1: Set Up Your Fireball Code

First, you need to register your Fireball executable with AiiDA:

```bash
verdi code setup
```

When prompted, provide:
- **Label**: `fireball@localhost` (or your preferred name)
- **Default input plugin**: `fireball`
- **Computer**: `localhost` (or your configured computer)
- **Filepath executable**: `/path/to/your/fireball/executable`

Alternatively, you can set up the code programmatically:

```python
from aiida import orm
from aiida.plugins import DataFactory

Code = DataFactory('code')

code = Code(
    input_plugin_name='fireball',
    remote_computer_exec=[computer, '/path/to/fireball/executable'],
)
code.label = 'fireball'
code.description = 'Fireball DFT code'
code.store()
```

## Step 2: Set Up Fdata Files

Fireball requires Fdata files containing pseudopotentials and basis sets. You'll need to set up a remote folder containing these files:

```python
from aiida import orm

# Create a remote folder for Fdata files
computer = orm.load_computer('localhost')  # or your computer

fdata_remote = orm.RemoteData()
fdata_remote.set_remote_path('/path/to/your/fdata/directory')
fdata_remote.computer = computer
fdata_remote.store()

print(f"Fdata remote folder created: PK={fdata_remote.pk}")
```

```{tip}
Your Fdata directory should contain subdirectories for each element (e.g., `C/`, `H/`, `O/`) with the corresponding `.pp` and `.na` files.
```

## Step 3: Create a Simple Structure

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

## Step 4: Set Up Calculation Parameters

Define the Fireball calculation parameters using the appropriate namelists:

```python
from aiida import orm

# Basic calculation parameters for silicon
parameters = {
    'OPTION': {
        'iimage': 1,        # Single point calculation
        'iquench': 0,       # No geometry optimization
        'dt': 0.25,         # Time step
        'nstepf': 1,        # Number of MD steps
        'ifixcharges': 1,   # Fix atomic charges
    },
    'OUTPUT': {
        'iwrtdos': 0,       # Don't write DOS
        'iwrtxyz': 1,       # Write position trajectory
    }
}

parameters_node = orm.Dict(dict=parameters)
parameters_node.store()
```

## Step 5: Set Up K-points

For silicon crystal, we need a reasonable k-point mesh:

```python
from aiida.plugins import DataFactory

KpointsData = DataFactory('core.array.kpoints')

kpoints = KpointsData()
# Use a reasonable k-point mesh for silicon
kpoints.set_kpoints_mesh([4, 4, 4], offset=[0.0, 0.0, 0.0])
kpoints.store()
```

## Step 6: Run the Calculation

Now we can set up and submit the calculation:

```python
from aiida.plugins import CalculationFactory
from aiida.engine import submit

# Load the calculation plugin
FireballCalculation = CalculationFactory('fireball')

# Load previously created nodes
code = orm.load_code('fireball@localhost')  # Use your code label

# Set up all inputs
inputs = {
    'code': code,
    'structure': structure,
    'parameters': parameters_node,
    'kpoints': kpoints,
    'fdata_remote': fdata_remote,
    'metadata': {
        'label': 'silicon_scf',
        'description': 'First Fireball calculation - silicon crystal',
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
calc_node = submit(FireballCalculation, **inputs)
print(f"Submitted calculation with PK={calc_node.pk}")
print(f"Monitor with: verdi process status {calc_node.pk}")
```

## Step 7: Monitor the Calculation

You can monitor your calculation using AiiDA's command-line tools:

```bash
# Check the status
verdi process status <PK>

# Watch the calculation in real-time
verdi process watch <PK>

# View the calculation log
verdi process report <PK>
```

## Step 8: Analyze the Results

Once the calculation is finished, you can access the results:

```python
# Load the calculation node
calc = orm.load_node(calc_node.pk)

# Check if it finished successfully
if calc.is_finished_ok:
    print("Calculation completed successfully!")
    
    # Access outputs
    if 'output_parameters' in calc.outputs:
        results = calc.outputs.output_parameters.get_dict()
        print("Output parameters:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    
    # Access retrieved files
    if 'retrieved' in calc.outputs:
        retrieved = calc.outputs.retrieved
        files = retrieved.list_object_names()
        print(f"Retrieved files: {files}")
        
        # Read output file content
        if 'output_fireball.log' in files:
            log_content = retrieved.get_object_content('output_fireball.log')
            print("Last 10 lines of output:")
            print('\n'.join(log_content.split('\n')[-10:]))
            
else:
    print(f"Calculation failed with state: {calc.process_state}")
    if calc.exit_message:
        print(f"Exit message: {calc.exit_message}")
```

## Understanding the Results

A successful Fireball calculation will produce several types of output:

### 1. Output Parameters

The `output_parameters` node contains extracted key results:

```python
results = calc.outputs.output_parameters.get_dict()

# Common output parameters include:
print(f"Total energy: {results.get('total_energy', 'N/A')} eV")
print(f"Number of atoms: {results.get('natoms', 'N/A')}")
print(f"Number of electrons: {results.get('nelectrons', 'N/A')}")
```

### 2. Retrieved Files

The calculation retrieves several files from the remote working directory:

- **`output_fireball.log`**: Main output file with calculation details
- **`input_fireball.bas`**: The input file that was actually used
- **`answer.out`**: Formatted output with key results
- Additional files depending on your `OUTPUT` settings

### 3. Structure Output

For geometry optimizations, you'll also get an optimized structure:

```python
if 'output_structure' in calc.outputs:
    final_structure = calc.outputs.output_structure
    print(f"Final structure has {len(final_structure.sites)} atoms")
```

## Common Issues and Solutions

### 1. Code Not Found
```
Error: Code 'fireball@localhost' not found
```
**Solution**: Check your code setup with `verdi code list` and verify the label.

### 2. Fdata Files Missing
```
Error: Cannot find Fdata files for element X
```
**Solution**: Verify your Fdata directory structure and paths.

### 3. Calculation Exceeds Walltime
```
Process finished with exit code 310
```
**Solution**: Increase `max_wallclock_seconds` in the metadata options.

### 4. Memory Issues
```
KILLED signal received
```
**Solution**: Increase memory allocation or use fewer CPU cores.

## Next Steps

Now that you've run your first calculation, you can:

- {doc}`optimization_tutorial`: Learn about geometry optimization
- {doc}`transport_tutorial`: Explore transport calculations  
- {doc}`transport_tutorial`: Learn advanced transport calculations
- {doc}`workflows`: Use automated workflows

## Script Summary

Here's the complete script for your first calculation:

```python
from aiida import orm
from aiida.plugins import DataFactory, CalculationFactory
from aiida.engine import submit

# Create structure
StructureData = DataFactory('structure')
structure = StructureData()
structure.set_cell([[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]])
structure.append_atom(position=[0.0, 0.0, 0.0], symbols='O')
structure.append_atom(position=[0.757, 0.587, 0.0], symbols='H')  
structure.append_atom(position=[-0.757, 0.587, 0.0], symbols='H')
structure.store()

# Set parameters
parameters = orm.Dict(dict={
    'OPTION': {'iimage': 1, 'iquench': 0, 'dt': 0.5, 'nstepf': 1},
    'OUTPUT': {'iwrtpop': 1, 'iwrtdos': 0, 'iwrtatom': 1}
})

# Set k-points
KpointsData = DataFactory('kpoints')
kpoints = KpointsData()
kpoints.set_kpoints_mesh([1, 1, 1])
kpoints.store()

# Set up Fdata (adjust path as needed)
computer = orm.load_computer('localhost')
fdata_remote = orm.RemoteData()
fdata_remote.set_remote_path('/path/to/fdata')
fdata_remote.computer = computer
fdata_remote.store()

# Submit calculation
FireballCalculation = CalculationFactory('fireball')
code = orm.load_code('fireball@localhost')

inputs = {
    'code': code,
    'structure': structure,
    'parameters': parameters,
    'kpoints': kpoints,
    'fdata_remote': fdata_remote,
    'metadata': {
        'label': 'water_first_calc',
        'options': {'resources': {'num_machines': 1}, 'max_wallclock_seconds': 600}
    }
}

calc_node = submit(FireballCalculation, **inputs)
print(f"Submitted: PK={calc_node.pk}")
```

Remember to adjust paths and computer names according to your setup!
