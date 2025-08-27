# AiiDA Fireball Documentation

Welcome to the documentation for the **AiiDA Fireball Plugin** - a comprehensive integration of the Fireball semi-empirical DFT code with the AiiDA computational workflow management platform.

```{image} _static/download.jpeg
:alt: AiiDA Fireball Quantum Simulation
:align: center
:width: 500px
```

## What is AiiDA Fireball?

AiiDA Fireball is a plugin that enables seamless execution and management of Fireball calculations within the AiiDA ecosystem. It provides:

- **Full Fireball Integration**: Complete support for Fireball semi-empirical DFT calculations
- **Advanced Transport Calculations**: State-of-the-art transport property calculations with flexible optional files
- **Workflow Automation**: Automated equation of state calculations and parameter optimization
- **Provenance Tracking**: Full data provenance and workflow reproducibility
- **High-Throughput Capabilities**: Designed for large-scale computational studies

## Installation

### Prerequisites

Before installing AiiDA Fireball, make sure you have:

- Python 3.8 or higher
- AiiDA 2.0 or higher
- Access to a computer with Fireball installed

### Install AiiDA Fireball

```bash
# Install from PyPI (when available)
pip install aiida-fireball

# Or install from source
git clone https://github.com/mohamedmamlouk/aiida-fireball.git
cd aiida-fireball
pip install -e .
```

### Setup AiiDA

If you haven't set up AiiDA yet:

```bash
# Quick setup
verdi quicksetup

# Or detailed setup
verdi setup
```

### Configure Computer and Code

```bash
# Setup computer
verdi computer setup

# Configure the computer
verdi computer configure <TRANSPORT> <COMPUTER_NAME>

# Setup Fireball code
verdi code setup

# Test the setup
verdi computer test <COMPUTER_NAME>
```

## Basic Usage

### Your First Calculation

```python
from aiida import orm, load_profile
from aiida_fireball import FireballCalculation

# Load AiiDA profile
load_profile()

# Create structure
structure = orm.StructureData()
# ... define your structure

# Create parameters
parameters = orm.Dict(dict={
    'max_scf_iterations': 100,
    'scf_tolerance': 1e-6,
    # ... other parameters
})

# Setup calculation
builder = FireballCalculation.get_builder()
builder.structure = structure
builder.parameters = parameters
builder.code = orm.load_code('fireball@computer')

# Submit calculation
from aiida.engine import submit
calc = submit(builder)
print(f"Submitted calculation with PK: {calc.pk}")
```

### Transport Calculations

```python
from aiida_fireball.workflows import TransportScanWorkChain

# Setup transport workflow
builder = TransportScanWorkChain.get_builder()
builder.fireball_code = orm.load_code('fireball@computer')
builder.structure = structure
builder.parameters = parameters

# Configure energy range
builder.energy_range = orm.Dict(dict={
    'start': -2.0,
    'end': 1.0, 
    'step': 0.1
})

# Submit workflow
workflow = submit(builder)
print(f"Submitted transport workflow with PK: {workflow.pk}")
```

## Examples

### Example 1: Single Point Calculation

```python
#!/usr/bin/env python
"""Example script for a single point calculation."""

from aiida import orm, load_profile
from aiida.engine import submit
from aiida_fireball import FireballCalculation

def main():
    load_profile()
    
    # Define structure (Water molecule example)
    structure = orm.StructureData()
    structure.append_atom(position=(0.0, 0.0, 0.0), symbols='O')
    structure.append_atom(position=(0.757, 0.587, 0.0), symbols='H')  
    structure.append_atom(position=(-0.757, 0.587, 0.0), symbols='H')
    structure.set_cell([10.0, 10.0, 10.0])
    
    # Set parameters
    parameters = orm.Dict(dict={
        'max_scf_iterations': 100,
        'scf_tolerance': 1e-6,
        'charge': 0,
        'spin': 1
    })
    
    # Setup and submit
    builder = FireballCalculation.get_builder()
    builder.structure = structure
    builder.parameters = parameters
    builder.code = orm.load_code('fireball@localhost')
    
    calc = submit(builder)
    print(f"Submitted calculation: {calc}")

if __name__ == '__main__':
    main()
```

### Example 2: Transport Property Scanning

```python
#!/usr/bin/env python
"""Example script for transport property scanning."""

from aiida import orm, load_profile
from aiida.engine import submit
from aiida_fireball.workflows import TransportScanWorkChain

def main():
    load_profile()
    
    # Load or create your structure
    structure = orm.load_node(STRUCTURE_PK)  # Replace with your structure PK
    
    # Setup workflow
    builder = TransportScanWorkChain.get_builder()
    builder.fireball_code = orm.load_code('fireball@localhost')
    builder.structure = structure
    
    # Transport-specific parameters
    builder.parameters = orm.Dict(dict={
        'max_scf_iterations': 100,
        'scf_tolerance': 1e-6,
        'transport': True
    })
    
    # Energy scanning range
    builder.energy_range = orm.Dict(dict={
        'start': -2.0,   # eV
        'end': 1.0,      # eV  
        'step': 0.1      # eV
    })
    
    workflow = submit(builder)
    print(f"Submitted transport workflow: {workflow}")

if __name__ == '__main__':
    main()
```

### Example 3: Analyzing Results

```python
#!/usr/bin/env python
"""Example script for analyzing calculation results."""

from aiida import orm, load_profile

def analyze_results(calc_pk):
    load_profile()
    
    # Load calculation
    calc = orm.load_node(calc_pk)
    
    # Check if finished
    if not calc.is_finished_ok:
        print("Calculation not finished successfully")
        return
    
    # Get results
    results = calc.outputs.output_parameters.get_dict()
    
    print("Calculation Results:")
    print(f"Total Energy: {results.get('total_energy', 'N/A')} eV")
    print(f"SCF Converged: {results.get('scf_converged', 'N/A')}")
    print(f"Number of SCF iterations: {results.get('scf_iterations', 'N/A')}")
    
    # Transport results (if available)
    if 'transport_properties' in calc.outputs:
        transport = calc.outputs.transport_properties.get_dict()
        print(f"Conductance: {transport.get('conductance', 'N/A')}")

if __name__ == '__main__':
    # Replace with your calculation PK
    analyze_results(CALC_PK)
```

## Key Features

### Calculation Types
- Single point energy calculations
- Geometry optimizations  
- Molecular dynamics
- Transport property calculations
- Band structure calculations

### Input Management
- Flexible parameter handling
- Optional file support (trans.optional, etc.)
- Automatic input validation
- Structure preprocessing

### Output Parsing
- Energy and forces extraction
- Electronic properties parsing
- Transport coefficients
- Error detection and reporting

### Workflow Integration
- WorkChain support for complex workflows
- Automatic restart capabilities  
- Error handling and recovery
- Results analysis tools

## Documentation Structure

```{toctree}
:maxdepth: 2
:caption: User Guide

user_guide/get_started
user_guide/tutorial
```

```{toctree}
:maxdepth: 2
:caption: Developer Guide

developer_guide/index
```

## Getting Help

- **Documentation**: This documentation site
- **Issues**: [GitHub Issues](https://github.com/mohamedmamlouk/aiida-fireball/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mohamedmamlouk/aiida-fireball/discussions)
- **AiiDA Community**: [AiiDA Discourse](https://aiida.discourse.group/)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/mohamedmamlouk/aiida-fireball/blob/main/CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/mohamedmamlouk/aiida-fireball/blob/main/LICENSE) for details.

## Acknowledgements

- The AiiDA development team
- The Fireball development team  
- All contributors to this project
