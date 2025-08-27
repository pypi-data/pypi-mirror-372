# Advanced Parallel Calculations Tutorial

This tutorial demonstrates advanced usage of the AiiDA Fireball plugin for parallel high-throughput calculations, using a real-world example of tungsten surface calculations with charge state variations.

## Overview

This example shows how to:
- Generate crystal surfaces using ASE integration
- Submit multiple calculations in parallel
- Handle HPC cluster configurations
- Use advanced Fireball parameters
- Apply system-level optimizations

## Complete Example: Tungsten (110) Surface with Charge States

This script generates a W(110) surface and submits parallel calculations for different charge states (`qstate` parameter):

```{literalinclude} ../../examples/submit_qstate_parallel.py
:language: python
:caption: submit_qstate_parallel.py - Parallel qstate calculations
```

## Detailed Explanation

### 1. Surface Generation with ASE

```python
from ase.build import bcc110
slab = bcc110('W', size=(1,1,15), a=3.1652, vacuum=20.0)
structure = StructureData(ase=slab)
```

**Key Parameters:**
- `'W'`: Tungsten element
- `size=(1,1,15)`: 1×1 surface with 15 layers
- `a=3.1652`: Lattice parameter in Angstroms
- `vacuum=20.0`: Vacuum space above surface

**Why This Works:**
- ASE provides robust crystal structure generation
- `StructureData(ase=slab)` converts seamlessly to AiiDA format
- 15 layers ensure bulk-like behavior in the center

### 2. HPC Configuration

```python
code = load_code('fireball_mpi@ruche')
fdata_remote = RemoteData(
    computer=code.computer,
    remote_path='/gpfs/workdir/mamloukm/fdata-WSSe/Fdata'
)
```

**HPC Setup:**
- `fireball_mpi@ruche`: MPI-enabled Fireball on 'ruche' cluster
- `RemoteData`: Points to shared filesystem Fdata directory
- Uses the same computer as the code for efficiency

### 3. High-Density K-Point Sampling

```python
kpoints = KpointsData()
kpoints.set_kpoints_mesh([15, 15, 1])
```

**Sampling Strategy:**
- `15×15×1`: Dense in-plane, single point perpendicular
- Appropriate for 2D surface calculations
- Ensures convergence for metallic systems

### 4. Charge State Scanning

```python
qstates = [0, 0.0078, 0.0156, 0.0233, 0.0311, 0.0389, 0.0467, 0.0545]
```

**Physical Meaning:**
- `qstate=0`: Neutral surface
- `qstate>0`: Positively charged surface
- Small increments for detailed charge response
- Useful for work function and electronic property studies

### 5. Advanced Fireball Parameters

```python
base_params = {
    "OPTION": {
        "nstepi":   1,      # Initial SCF steps
        "nstepf":   5000,   # Maximum MD/optimization steps
        "icluster": 0,      # Periodic boundary conditions
        "iquench":  -1,     # Quenching method (-1 = advanced)
        "iqout":    1,      # Output frequency
        "dt":       0.25,   # Time step (fs)
        "itrans":   0,      # No transport calculation
    },
    "OUTPUT": {
        "iwrtxyz":     0,   # No XYZ trajectory
        "iwrtdos":     0,   # No DOS output
        "iwrteigen":   0,   # No eigenvalue output
        "iwrtcdcoefs": 0,   # No coefficients output
    },
}
```

**Parameter Optimization:**
- Small time step (`dt=0.25`) for stable dynamics
- High step limit (`nstepf=5000`) for convergence
- Minimal output to reduce I/O overhead
- Periodic boundaries for surface slab

### 6. Builder Pattern Usage

```python
builder = FireballCalculation.get_builder()
builder.code         = code
builder.structure    = structure
builder.kpoints      = kpoints
builder.parameters   = parameters
builder.fdata_remote = fdata_remote
```

**Advantages:**
- Clean, readable code structure
- Type checking and validation
- Easy parameter modification
- Consistent interface

### 7. HPC Resource Management

```python
builder.metadata.options.queue_name            = "cpu_long"
builder.metadata.options.max_wallclock_seconds = 168 * 3600  # 1 week
builder.metadata.options.resources = {
    "num_machines":             1,
    "num_mpiprocs_per_machine": 1,
    "num_cores_per_machine":    1,
}
```

**Resource Strategy:**
- `cpu_long`: Long-running queue for convergence
- 1 week walltime for large surface calculations
- Single-core for memory-intensive DFT
- Scales to multi-core if needed

### 8. System-Level Optimization

```python
builder.metadata.options.prepend_text = """
# Remove quotes around qstate
sed -i "s/\\(qstate *= *\\)'\\([0-9.]*d0\\)'/\\1\\2/" fireball.in
"""
```

**Why This Is Needed:**
- Fireball expects numeric values without quotes
- AiiDA may add quotes during serialization
- `sed` command fixes formatting before execution
- Ensures compatibility with Fireball parser

## Monitoring and Analysis

### Tracking Submissions

```python
submitted_calcs = []
for q in qstates:
    # ... setup code ...
    calc = submit(builder)
    submitted_calcs.append((q, calc))
    print(f"  • qstate={q} → PK={calc.pk}", flush=True)
```

### Monitoring Progress

```bash
# Check all running calculations
verdi process list -a

# Monitor specific calculation
verdi process watch <PK>

# Check calculation status
for pk in 12345 12346 12347; do
    echo "PK $pk: $(verdi process status $pk)"
done
```

### Collecting Results

```python
def collect_qstate_results(submitted_calcs):
    """Collect results from qstate calculations."""
    results = {}
    
    for qstate, calc_node in submitted_calcs:
        if calc_node.is_finished_ok:
            output_params = calc_node.outputs.output_parameters.get_dict()
            results[qstate] = {
                'total_energy': output_params.get('total_energy'),
                'final_structure': calc_node.outputs.output_structure,
                'pk': calc_node.pk
            }
        else:
            print(f"Warning: qstate={qstate} calculation failed")
    
    return results

# Usage
results = collect_qstate_results(submitted_calcs)

# Plot energy vs charge state
import matplotlib.pyplot as plt
qstates = sorted(results.keys())
energies = [results[q]['total_energy'] for q in qstates]

plt.plot(qstates, energies, 'bo-')
plt.xlabel('Charge State (qstate)')
plt.ylabel('Total Energy (eV)')
plt.title('W(110) Surface Energy vs Charge State')
plt.show()
```

## Advanced Variations

### 1. Structure Optimization

For geometry optimization, modify parameters:

```python
base_params["OPTION"].update({
    "iquench": 1,     # Enable optimization
    "iimage": 2,      # Optimization mode
    "nstepf": 1000,   # Optimization steps
})
```

### 2. Different Surface Orientations

```python
# Various tungsten surfaces
surfaces = {
    '100': bcc100('W', size=(2,2,10), a=3.1652, vacuum=15.0),
    '110': bcc110('W', size=(1,1,15), a=3.1652, vacuum=20.0),
    '111': fcc111('W', size=(2,2,10), a=3.1652, vacuum=15.0),  # Note: W is BCC, this is hypothetical
}

for surface_name, slab in surfaces.items():
    structure = StructureData(ase=slab)
    # Submit calculations...
```

### 3. Temperature Scanning

```python
temperatures = [100, 200, 300, 400, 500]  # Kelvin

for T in temperatures:
    params = {**base_params}
    params["OPTION"]["T_initial"] = T
    params["OPTION"]["T_final"] = T
    # Submit with temperature variation...
```

### 4. Work Function Calculations

Combine with electric field for work function:

```python
# Add electric field in z-direction
params["OPTION"]["iefield"] = 1      # Enable electric field
params["OPTION"]["efield"] = 0.001   # Field strength (a.u.)
```

## Performance Optimization

### 1. Efficient Resource Allocation

```python
# For large systems
if num_atoms > 100:
    resources = {
        "num_machines": 2,
        "num_mpiprocs_per_machine": 8,
        "num_cores_per_machine": 8,
    }
    walltime = 7 * 24 * 3600  # 1 week
else:
    resources = {
        "num_machines": 1,
        "num_mpiprocs_per_machine": 4,
        "num_cores_per_machine": 4,
    }
    walltime = 24 * 3600  # 1 day
```

### 2. Memory Management

```python
# For memory-intensive calculations
builder.metadata.options.custom_scheduler_commands = """
#SBATCH --mem=32GB
#SBATCH --mem-per-cpu=4GB
"""
```

### 3. I/O Optimization

```python
# Reduce output for large parameter sweeps
minimal_output = {
    "iwrtxyz": 0,     # No trajectory
    "iwrtdos": 0,     # No DOS
    "iwrteigen": 0,   # No eigenvalues
    "iwrtpop": 0,     # No population analysis
}
```

## Error Handling and Robustness

### 1. Automatic Restart

```python
def submit_with_restart(builder, max_restarts=2):
    """Submit calculation with automatic restart on failure."""
    for attempt in range(max_restarts + 1):
        calc = submit(builder)
        
        # Wait for completion (in real scenario, use daemon)
        while not calc.is_terminated:
            time.sleep(60)
        
        if calc.is_finished_ok:
            return calc
        
        if attempt < max_restarts:
            print(f"Calculation failed, restarting (attempt {attempt + 1})")
            # Modify parameters for restart
            builder.metadata.options.max_wallclock_seconds *= 2
    
    raise RuntimeError("Calculation failed after all restart attempts")
```

### 2. Validation Before Submission

```python
def validate_surface_calculation(structure, parameters):
    """Validate parameters before submission."""
    
    # Check surface has vacuum
    cell = structure.cell
    if cell[2][2] < 15.0:
        raise ValueError("Insufficient vacuum space for surface calculation")
    
    # Check k-points for 2D system
    kpoints_mesh = parameters.get('kpoints_mesh', [1, 1, 1])
    if kpoints_mesh[2] != 1:
        print("Warning: Using multiple k-points perpendicular to surface")
    
    # Check charge state range
    qstate = parameters.get('OPTION', {}).get('qstate', 0)
    if abs(qstate) > 0.1:
        print(f"Warning: Large charge state {qstate} may cause convergence issues")
```

## Integration with Workflows

This example can be integrated into larger workflows:

```python
from aiida.engine import WorkChain, ToContext

class QstateScanWorkChain(WorkChain):
    """Workflow for systematic qstate scanning."""
    
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input('code', valid_type=Code)
        spec.input('structure', valid_type=StructureData)
        spec.input('qstate_range', valid_type=List)
        spec.output('qstate_results', valid_type=Dict)
    
    def setup(self):
        """Initialize workflow."""
        self.ctx.calculations = {}
    
    def submit_qstate_calculations(self):
        """Submit all qstate calculations."""
        for q in self.inputs.qstate_range:
            # Setup calculation as in example
            calc = self.submit(FireballCalculation, **inputs)
            self.ctx.calculations[q] = calc
    
    def collect_results(self):
        """Collect and analyze results."""
        results = {}
        for q, calc in self.ctx.calculations.items():
            if calc.is_finished_ok:
                results[q] = calc.outputs.output_parameters.get_dict()
        
        self.out('qstate_results', Dict(dict=results))
```

## Next Steps

- {doc}`../user_guide/workflows`: Learn about automated workflows
- {doc}`../user_guide/transport_tutorial`: Advanced transport calculations
- {doc}`../reference/index`: Complete API reference

This example demonstrates the power and flexibility of the AiiDA Fireball plugin for advanced computational materials science workflows.
