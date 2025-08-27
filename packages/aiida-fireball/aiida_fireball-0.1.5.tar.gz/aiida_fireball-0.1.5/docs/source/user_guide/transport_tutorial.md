# Transport Calculations Tutorial

This comprehensive tutorial will guide you through setting up and running advanced transport calculations with the AiiDA Fireball plugin.

## Overview

The AiiDA Fireball plugin supports sophisticated transport property calculations through four optional files:

- **interaction.optional** - Defines interaction parameters between electrodes
- **eta.optional** - Specifies energy broadening parameters  
- **trans.optional** - Controls transport calculation settings
- **bias.optional** - Sets bias voltage parameters

## Prerequisites

Before starting, ensure you have:
- ✅ AiiDA Fireball plugin installed and configured
- ✅ Fireball code set up with `verdi code setup`
- ✅ Fdata files configured (see {doc}`installation`)
- ✅ Basic understanding of {doc}`first_calculation`

## Transport System Setup

### 1. Create a Transport-Ready Structure

For transport calculations, you typically need a structure that represents a molecular junction or extended system:

```python
from aiida import orm
from aiida.plugins import DataFactory

StructureData = DataFactory('structure')

# Create a carbon chain for transport
structure = StructureData()
structure.set_cell([[20.0, 0.0, 0.0], 
                   [0.0, 15.0, 0.0], 
                   [0.0, 0.0, 15.0]])

# Create a 5-atom carbon chain
for i in range(5):
    structure.append_atom(position=[i * 1.4, 0.0, 0.0], symbols='C')

structure.store()
```

### 2. Set Up Basic Calculation Parameters

```python
from aiida.plugins import CalculationFactory

FireballCalculation = CalculationFactory('fireball')

# Basic Fireball parameters for transport calculations
basic_parameters = {
    'OPTION': {
        'iimage': 1,         # Single point calculation
        'iquench': 0,        # No geometry optimization
        'dt': 0.5,           # Time step (not critical for single point)
        'nstepf': 1,         # Single step for SCF
    },
    'OUTPUT': {
        'iwrtpop': 1,        # Write population analysis
        'iwrttrans': 1,      # Enable transport output (essential!)
        'iwrtatom': 1,       # Write atomic information
    }
}
```

## Transport Parameter Configuration

The transport parameters are specified in the `settings` input using the `TRANSPORT` namespace:

### 3. INTERACTION Parameters

These define the interaction between the molecular system and electrodes:

```python
interaction_params = {
    'ncell1': 0,          # Number of cells for electrode 1
    'total_atoms1': 5,    # Total atoms in electrode 1 region
    'ninterval1': 1,      # Number of intervals for electrode 1
    'intervals1': [[1, 5]], # Start and end atom indices
    'natoms_tip1': 2,     # Number of tip atoms for electrode 1
    'atoms1': [1, 2],     # Tip atom indices for electrode 1
    
    # Same parameters for electrode 2
    'ncell2': 0,
    'total_atoms2': 5,
    'ninterval2': 1,
    'intervals2': [[4, 5]],
    'natoms_tip2': 2,
    'atoms2': [4, 5]
}
```

**Parameter Explanation:**
- `ncell1/2`: Number of unit cells for periodic electrodes (0 for molecules)
- `total_atoms1/2`: Total number of atoms in each electrode region
- `intervals1/2`: List of [start, end] atom ranges for each electrode
- `atoms1/2`: Specific atom indices that act as electrode tips

### 4. ETA Parameters

Control energy broadening for the Green's functions:

```python
eta_params = {
    'imag_part': 0.01,           # Imaginary part for broadening (eV)
    'intervals': [[1, 2], [4, 5]] # Energy intervals for eta calculation
}
```

**Parameter Explanation:**
- `imag_part`: Small imaginary component added to energy (typically 0.01-0.1 eV)
- `intervals`: Energy ranges where eta broadening is applied

### 5. TRANS Parameters

Core transport calculation settings:

```python
trans_params = {
    'ieta': True,           # Use eta broadening
    'iwrt_trans': True,     # Write transport coefficients  
    'ichannel': False,      # Calculate transmission channels
    'ifithop': 1,           # Fitting method (0 or 1)
    'Ebottom': -2.0,        # Bottom of energy range (eV)
    'Etop': 2.0,            # Top of energy range (eV)
    'nsteps': 100,          # Number of energy steps
    'eta': 0.01             # Broadening parameter (eV)
}
```

**Parameter Explanation:**
- `ieta/iwrt_trans/ichannel`: Boolean flags for different transport features
- `ifithop`: Method for fitting (0=direct, 1=iterative)
- Energy range defines where transmission is calculated
- `nsteps`: Resolution of energy grid

### 6. BIAS Parameters

Bias voltage and electrostatic potential:

```python
bias_params = {
    'bias': 1.0,      # Applied bias voltage (V)
    'z_top': 10.0,    # Top z-coordinate for bias region
    'z_bottom': 0.0   # Bottom z-coordinate for bias region
}
```

## Complete Transport Calculation

### 7. Combine All Parameters

```python
# Complete settings dictionary
transport_settings = {
    'TRANSPORT': {
        'INTERACTION': interaction_params,
        'ETA': eta_params,
        'TRANS': trans_params,
        'BIAS': bias_params
    }
}

# Set up all inputs
inputs = {
    'code': code,
    'structure': structure,
    'parameters': orm.Dict(dict=basic_parameters),
    'kpoints': kpoints,
    'fdata_remote': fdata_remote,
    'settings': orm.Dict(dict=transport_settings),
    'metadata': {
        'label': 'carbon_chain_transport',
        'description': 'Transport calculation for 5-atom carbon chain',
        'options': {
            'resources': {'num_machines': 1},
            'max_wallclock_seconds': 3600,
        }
    }
}
```

### 8. Submit and Monitor

```python
from aiida.engine import submit

# Submit the calculation
calc_node = submit(FireballCalculation, **inputs)
print(f"Submitted transport calculation with PK={calc_node.pk}")

# Monitor progress
print(f"Monitor with: verdi process status {calc_node.pk}")
print(f"Watch output: verdi process watch {calc_node.pk}")
```

## Analyzing Transport Results

### 9. Access Generated Files

The calculation will generate the optional files:

```python
# After calculation completes
calc = orm.load_node(calc_node.pk)

if calc.is_finished_ok:
    retrieved = calc.outputs.retrieved
    
    # List generated transport files
    files = retrieved.list_object_names()
    transport_files = [f for f in files if f.endswith('.optional')]
    
    print("Generated transport files:")
    for tf in transport_files:
        print(f"  - {tf}")
        
    # Read a specific transport file
    if 'trans.optional' in files:
        trans_content = retrieved.get_object_content('trans.optional')
        print("Transport parameters:")
        print(trans_content)
```

### 10. Extract Transport Properties

```python
# Get parsed results
if 'output_parameters' in calc.outputs:
    results = calc.outputs.output_parameters.get_dict()
    
    # Look for transport-related outputs
    transport_keys = [k for k in results.keys() if 'transport' in k.lower()]
    
    if transport_keys:
        print("Transport properties found:")
        for key in transport_keys:
            print(f"  {key}: {results[key]}")
    
    # Check for transmission data
    if 'transmission' in results:
        transmission = results['transmission']
        print(f"Transmission coefficient: {transmission}")
```

## Advanced Transport Scenarios

### Selective Transport Files

You can generate only specific transport files by including only the relevant parameters:

```python
# Only eta and trans files
selective_transport = {
    'TRANSPORT': {
        'ETA': eta_params,
        'TRANS': trans_params
        # No INTERACTION or BIAS - those files won't be generated
    }
}
```

## Troubleshooting Transport Calculations

### Common Issues

1. **Missing mandatory keys**: Ensure all required parameters are present in each transport block
2. **Atom indexing**: Fireball uses 1-based indexing (atom 1, 2, 3, ...)
3. **Energy ranges**: Check that `Ebottom < Etop` and the range covers relevant energies
4. **Convergence**: Increase `nsteps` for better energy resolution

### Validation Tips

```python
# Check parameter completeness before submission
def validate_transport_params(transport_dict):
    """Validate transport parameters before submission."""
    
    if 'INTERACTION' in transport_dict:
        required = ['ncell1', 'total_atoms1', 'ninterval1', 'intervals1', 
                   'natoms_tip1', 'atoms1', 'ncell2', 'total_atoms2', 
                   'ninterval2', 'intervals2', 'natoms_tip2', 'atoms2']
        
        missing = [k for k in required if k not in transport_dict['INTERACTION']]
        if missing:
            print(f"Missing INTERACTION keys: {missing}")
            return False
    
    if 'TRANS' in transport_dict:
        trans = transport_dict['TRANS']
        if trans['Ebottom'] >= trans['Etop']:
            print("Error: Ebottom must be less than Etop")
            return False
            
    return True

# Use before submission
if validate_transport_params(transport_settings['TRANSPORT']):
    calc_node = submit(FireballCalculation, **inputs)
```

## Next Steps

- {doc}`workflows`: Learn about automated transport workflows
- {doc}`../user_guide/workflows`: Learn about automated workflows
- {doc}`../reference/calculations`: Detailed API reference

```{seealso}
For more advanced transport theory and Fireball-specific details, consult the [Fireball manual](https://fireball-qmd.github.io/fireball.html) and related transport calculation literature.
```
