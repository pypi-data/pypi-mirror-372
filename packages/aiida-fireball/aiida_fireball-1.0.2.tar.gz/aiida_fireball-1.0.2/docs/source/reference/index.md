# API Reference

This section provides detailed reference documentation for all components of the AiiDA Fireball plugin.

## Overview

The AiiDA Fireball plugin provides the following main components:

- **Calculations**: FireballCalculation class for running Fireball DFT calculations
- **Parsers**: FireballParser and RawParser for processing outputs
- **Workflows**: BirchMurnaghanRelaxWorkChain for equation of state calculations

## Plugin Architecture

### Entry Points

The plugin registers the following entry points:

**Calculations:**
- `fireball`: Main Fireball calculation class

**Parsers:**
- `fireball`: Default Fireball output parser  
- `fireball.raw`: Raw file parser

**Workflows:**
- `fireball.birch_murnaghan_relax`: Birch-Murnaghan equation of state workflow

## Main Classes

### FireballCalculation

The main calculation class that handles:
- Input file generation for Fireball
- Transport parameter processing
- Optional file generation (interaction.optional, eta.optional, trans.optional, bias.optional)
- Job submission and monitoring

**Key Methods:**
- `prepare_for_submission()`: Prepares calculation inputs
- `_generate_input_file()`: Creates main Fireball input file
- `_generate_*_optional()`: Creates transport parameter files

### FireballParser

Output parser that extracts:
- Total energies and forces
- Electronic structure information
- Transport properties (when available)
- Convergence information

### Data Types and Inputs

**Required Inputs:**
- `code`: AiiDA Code node pointing to Fireball executable
- `structure`: AiiDA StructureData with atomic positions
- `parameters`: Dict with Fireball calculation parameters
- `kpoints`: KpointsData for k-point sampling
- `fdata_remote`: RemoteData pointing to Fireball basis sets

**Optional Inputs:**
- `settings`: Dict with transport parameters and other settings
- `metadata`: Calculation metadata (resources, walltime, etc.)

**Output Types:**
- `output_parameters`: Dict with extracted results
- `output_structure`: Final structure (for optimizations)
- `retrieved`: Retrieved files from calculation

## Parameter Structure

### Basic Parameters

```python
parameters = {
    'OPTION': {
        'iimage': 1,      # Calculation type (1=SCF, 2=optimization)
        'iquench': 0,     # Optimization method
        'dt': 0.5,        # Time step
        'nstepf': 100,    # Number of steps
    },
    'OUTPUT': {
        'iwrtpop': 1,     # Population analysis
        'iwrtdos': 1,     # Density of states  
        'iwrtatom': 1,    # Atomic information
    }
}
```

### Transport Parameters

Transport calculations use the `settings` input with `TRANSPORT` namespace:

```python
transport_settings = {
    'TRANSPORT': {
        'INTERACTION': {
            'ncell1': 0,
            'total_atoms1': 5,
            'ninterval1': 1,
            'intervals1': [[1, 5]],
            'natoms_tip1': 2,
            'atoms1': [1, 2],
            # Similar parameters for electrode 2
        },
        'ETA': {
            'imag_part': 0.01,
            'intervals': [[1, 2], [4, 5]]
        },
        'TRANS': {
            'ieta': True,
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
```

## Usage Examples

### Basic Calculation

```python
from aiida import orm
from aiida.plugins import CalculationFactory
from aiida.engine import submit

FireballCalculation = CalculationFactory('fireball')

inputs = {
    'code': orm.load_code('fireball@localhost'),
    'structure': structure,
    'parameters': parameters,
    'kpoints': kpoints,
    'fdata_remote': fdata_remote,
}

calc_node = submit(FireballCalculation, **inputs)
```

### Transport Calculation

```python
inputs['settings'] = orm.Dict(dict=transport_settings)
calc_node = submit(FireballCalculation, **inputs)
```

## Error Handling

The plugin defines custom exceptions for error handling and provides detailed error messages for common issues like:
- Missing Fdata files
- Invalid parameter combinations  
- Transport parameter validation errors
- Calculation convergence problems

For detailed examples and tutorials, see the [User Guide](../user_guide/index.md) section.
