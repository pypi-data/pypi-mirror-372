# Examples Directory

This directory contains working examples demonstrating the use of the AiiDA Fireball plugin.

## Available Examples

### 1. Setup Fdata (`setup_fdata.py`)
Helper script to set up Fdata remote folder:
- Upload Fdata directory to AiiDA
- Create RemoteData node for Fireball calculations
- List existing Fdata remote folders

```bash
# Setup new Fdata remote
python setup_fdata.py /path/to/your/Fdata

# List existing Fdata remotes
python setup_fdata.py list
```

### 2. Structure Optimization (`optimization.py`)
Geometry optimization example showing:
- Setting up a H₂O molecule structure  
- Configuring Fireball optimization parameters (iimage=2, iquench=1)
- Analyzing optimization trajectories and results

```bash
# Run the optimization
python optimization.py

# Analyze results (after completion)
python optimization.py analyze <calc_pk>
```

### 3. Transport Calculations (`transport_calculation.py`)
Advanced transport property calculations demonstrating:
- All transport optional files (interaction.optional, eta.optional, trans.optional, bias.optional)
- Carbon chain transport calculations
- Proper TRANSPORT parameter structure in settings

```bash
python transport_calculation.py
```

## Prerequisites

Before running these examples, ensure you have:

1. **AiiDA Profile Setup**:
   ```bash
   verdi profile setup
   verdi daemon start
   ```

2. **Computer Configuration**:
   ```bash
   verdi computer setup
   verdi computer configure local localhost
   ```

3. **Code Setup**:
   ```bash
   verdi code setup
   # Configure with your Fireball executable path
   ```

4. **Fdata Setup**:
   ```bash
   # Use the helper script to set up Fdata
   python setup_fdata.py /path/to/your/Fdata
   ```

## Parameter Reference

### Transport Parameters

The transport calculations use the TRANSPORT namespace with four sub-blocks:

#### INTERACTION Parameters
- `ncell1`, `ncell2`: Number of cells for each sample
- `total_atoms1`, `total_atoms2`: Total atoms in each sample
- `ninterval1`, `ninterval2`: Number of intervals
- `intervals1`, `intervals2`: List of interval pairs [start, end]
- `natoms_tip1`, `natoms_tip2`: Number of tip atoms
- `atoms1`, `atoms2`: List of atom indices

#### ETA Parameters  
- `imag_part`: Imaginary part value
- `intervals`: List of interval pairs for eta calculation

#### TRANS Parameters
- `ieta`: Boolean flag for eta calculation
- `iwrt_trans`: Boolean flag for writing transport data
- `ichannel`: Boolean flag for channel calculation
- `ifithop`: Integer flag (0 or 1)
- `Ebottom`, `Etop`: Energy range (eV)
- `nsteps`: Number of energy steps
- `eta`: Broadening parameter

#### BIAS Parameters
- `bias`: Bias voltage value
- `z_top`: Top z-coordinate
- `z_bottom`: Bottom z-coordinate

### Optimization Parameters

The optimization calculations use Fireball's native namelists:

#### OPTION Namelist
- `iimage`: Calculation type (2 for MD with optimization)
- `iquench`: Quench forces flag (1 to optimize)
- `dt`: Time step in femtoseconds
- `nstepf`: Maximum number of optimization steps

#### OUTPUT Namelist
- `iwrtfpieces`: Write forces to output
- `iwrtpop`: Write population analysis

## Output Analysis

All calculations generate standard AiiDA output nodes that can be analyzed:

```python
from aiida import orm

# Load a completed calculation
calc = orm.load_node(pk)

# Check outputs
print(calc.outputs)

# Get parsed results
if 'output_parameters' in calc.outputs:
    results = calc.outputs.output_parameters.get_dict()
    print(results)

# For optimization: get final structure
if 'output_structure' in calc.outputs:
    final_structure = calc.outputs.output_structure
    print(f"Optimized structure PK: {final_structure.pk}")
```

## Troubleshooting

1. **Code not found**: Ensure your Fireball code is properly configured with `verdi code setup`
2. **Computer issues**: Verify computer configuration with `verdi computer test localhost`
3. **Calculation failures**: Check logs with `verdi process report <pk>`
4. **Transport parameter errors**: Ensure all required TRANSPORT sub-blocks have complete parameters

For more help, see the [documentation](https://aiida-fireball.readthedocs.io/) or open an issue on GitHub.
