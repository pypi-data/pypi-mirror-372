# Your First Fireball Calculation

This tutorial will guide you through running your first Fireball calculation using the AiiDA Fireball plugin. We'll calculate the electronic structure of a simple H₂ molecule.

## Prerequisites

Before starting, ensure you have:
- ✅ AiiDA Fireball plugin installed
- ✅ AiiDA profile configured
- ✅ Fireball code set up
- ✅ Computer configured

If you haven't completed these steps, see the [Installation Guide](installation.md).

## Step 1: Set Up Your Environment

Start by importing the necessary AiiDA components:

```python
from aiida import orm, engine
from aiida.plugins import CalculationFactory, DataFactory

# Load the Fireball calculation plugin
FireballCalculation = CalculationFactory('fireball')
StructureData = DataFactory('structure')
```

## Step 2: Create a Molecular Structure

Let's create a simple H₂ molecule structure:

```python
# Initialize the structure
structure = StructureData()

# Define the simulation cell (10 Å cubic cell)
cell = [
    [10.0, 0.0, 0.0],
    [0.0, 10.0, 0.0], 
    [0.0, 0.0, 10.0]
]
structure.set_cell(cell)

# Add two hydrogen atoms with realistic H-H bond length (0.74 Å)
structure.append_atom(position=[0.0, 0.0, 0.0], symbols='H')
structure.append_atom(position=[0.74, 0.0, 0.0], symbols='H')

# Store the structure in the database
structure.store()
print(f"Structure created with PK={structure.pk}")
```

## Step 3: Load Your Fireball Code

Load the Fireball code you configured during installation:

```python
# Load the code (replace with your actual code label)
code = orm.load_code('fireball-v3.0@localhost')
print(f"Using code: {code.label}")
```

## Step 4: Prepare Calculation Inputs

Set up the inputs for your Fireball calculation:

```python
inputs = {
    'code': code,
    'structure': structure,
    'metadata': {
        'label': 'H2_molecule_first_calc',
        'description': 'My first H2 molecule calculation with AiiDA Fireball',
        'options': {
            'resources': {
                'num_machines': 1,
                'num_mpiprocs_per_machine': 1,
            },
            'max_wallclock_seconds': 1800,  # 30 minutes
        }
    }
}

print("Calculation inputs prepared ✓")
```

## Step 5: Submit the Calculation

Submit your calculation to the AiiDA daemon:

```python
# Submit the calculation
calc_node = engine.submit(FireballCalculation, **inputs)
print(f"Calculation submitted with PK={calc_node.pk}")
print(f"Monitor progress with: verdi process status {calc_node.pk}")
```

## Step 6: Monitor the Calculation

While your calculation runs, you can monitor its progress:

```bash
# Check calculation status
verdi process status <PK>

# Watch real-time updates
verdi process watch <PK>

# View calculation details
verdi process show <PK>
```

The calculation should complete within a few minutes for this simple system.

## Step 7: Analyze the Results

Once the calculation finishes, examine the results:

```python
# Load the completed calculation
calc = orm.load_node(<PK>)  # Replace <PK> with your calculation's PK

# Check if calculation completed successfully
if calc.is_finished_ok:
    print(" Calculation completed successfully!")
    
    # Access output files
    if 'retrieved' in calc.outputs:
        retrieved = calc.outputs.retrieved
        print(f"Retrieved files: {retrieved.list_object_names()}")
    
    # Access parsed results (if parser was successful)
    if 'output_parameters' in calc.outputs:
        results = calc.outputs.output_parameters.get_dict()
        print("Parsed results:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    
    # Check for output structure (for relaxation calculations)
    if 'output_structure' in calc.outputs:
        final_structure = calc.outputs.output_structure
        print(f"Final structure available with PK={final_structure.pk}")
        
else:
    print(" Calculation failed!")
    print(f"Exit status: {calc.exit_status}")
    print(f"Exit message: {calc.exit_message}")
```

## Step 8: Examine Generated Files

The Fireball calculation generates several files. Let's examine them:

```python
# Get the calculation's working directory content
if calc.is_finished:
    # Access retrieved folder
    retrieved = calc.outputs.retrieved
    
    # List all files
    files = retrieved.list_object_names()
    print("Generated files:")
    for file in files:
        print(f"  📄 {file}")
    
    # Read specific files (example: input file)
    if 'aiida.in' in files:
        input_content = retrieved.get_object_content('aiida.in')
        print("\nGenerated input file (aiida.in):")
        print("="*40)
        print(input_content)
```

## Understanding the Output

A successful Fireball calculation typically produces:

### Key Output Files
- **`aiida.in`**: Generated input file
- **`aiida.bas`**: Basis set information  
- **`aiida.lvs`**: Lattice vectors
- **`aiida.kpts`**: K-point sampling (if applicable)
- **Output files**: Various calculation results

### Parsed Results
The parser extracts key information such as:
- Total energy
- Forces on atoms
- Electronic properties
- Convergence information

## Common First-Calculation Issues

### Issue 1: Code Not Found
```bash
# Error: Code 'fireball-v3.0@localhost' not found
# Solution: Check your code setup
verdi code list
verdi code show fireball-v3.0@localhost
```

### Issue 2: Computer Configuration
```bash
# Error: Transport/scheduler issues  
# Solution: Test your computer
verdi computer test localhost
```

### Issue 3: Calculation Fails
```python
# Check detailed error information
calc = orm.load_node(<PK>)
print(f"Exit status: {calc.exit_status}")
print(f"Exit message: {calc.exit_message}")

# Check scheduler output
if 'retrieved' in calc.outputs:
    retrieved = calc.outputs.retrieved
    if '_scheduler-stderr.txt' in retrieved.list_object_names():
        stderr = retrieved.get_object_content('_scheduler-stderr.txt')
        print("Scheduler stderr:", stderr)
```

## Next Steps

Congratulations! You've run your first Fireball calculation. Now you can:

1. **[Explore Transport Calculations](transport_tutorial.md)** - Learn advanced transport properties
2. **[Try Different Systems](../examples/README.md)** - Explore more complex structures  
3. **[Use Workflows](workflows.md)** - Automate parameter studies
4. **[Customize Parameters](parameters.md)** - Fine-tune your calculations

## Complete Example Script

Here's a complete script combining all the steps:

```python
#!/usr/bin/env python3
"""
Complete first Fireball calculation example
"""
from aiida import orm, engine
from aiida.plugins import CalculationFactory, DataFactory

def run_first_calculation():
    # Load plugins
    FireballCalculation = CalculationFactory('fireball')
    StructureData = DataFactory('structure')
    
    # Create H2 molecule
    structure = StructureData()
    structure.set_cell([[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]])
    structure.append_atom(position=[0.0, 0.0, 0.0], symbols='H')
    structure.append_atom(position=[0.74, 0.0, 0.0], symbols='H')
    structure.store()
    
    # Load code
    code = orm.load_code('fireball-v3.0@localhost')
    
    # Prepare inputs
    inputs = {
        'code': code,
        'structure': structure,
        'metadata': {
            'label': 'H2_first_calculation',
            'options': {
                'resources': {'num_machines': 1},
                'max_wallclock_seconds': 1800,
            }
        }
    }
    
    # Submit calculation
    calc_node = engine.submit(FireballCalculation, **inputs)
    print(f"Submitted calculation PK={calc_node.pk}")
    
    return calc_node

if __name__ == '__main__':
    calc = run_first_calculation()
    print(f"Monitor with: verdi process status {calc.pk}")
```

Save this as `first_calculation.py` and run:

```bash
python first_calculation.py
```

Happy calculating! 🚀
