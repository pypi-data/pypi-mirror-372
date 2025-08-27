# Automated Workflows

The AiiDA Fireball plugin provides several automated workflows to streamline complex calculations and common computational tasks.

## Overview

Workflows in AiiDA are powerful tools that:
- Automate complex multi-step calculations
- Handle error recovery and restarts
- Provide reproducible computational protocols
- Scale calculations across different systems

The plugin currently includes:
- **Birch-Murnaghan EOS**: Equation of state calculations
- **Transport workflows**: Automated transport property calculations (planned)
- **Optimization workflows**: Advanced geometry optimization protocols (planned)

## Birch-Murnaghan Equation of State

The `BirchMurnaghanRelaxWorkChain` automatically calculates the equation of state by:

1. Generating structures at different volumes
2. Running geometry optimizations for each volume
3. Extracting energies and fitting to Birch-Murnaghan equation
4. Computing bulk modulus and equilibrium volume

### Basic Usage

```python
from aiida import orm
from aiida.plugins import WorkflowFactory
from aiida.engine import submit

# Load the workflow
BirchMurnaghanWorkChain = WorkflowFactory('fireball.birch_murnaghan_relax')

# Required inputs
inputs = {
    'code': orm.load_code('fireball@localhost'),
    'structure': structure,  # Your initial structure
    'fdata_remote': fdata_remote,  # Fdata files location
    'base_parameters': orm.Dict(dict={
        'OPTION': {
            'iimage': 2,      # Geometry optimization
            'iquench': 1,     # Quenching method
            'dt': 0.5,        # Time step
            'nstepf': 100,    # Maximum steps
        },
        'OUTPUT': {
            'iwrtpop': 1,     # Population analysis
            'iwrtatom': 1,    # Atomic information
        }
    }),
    'volume_range': orm.Dict(dict={
        'min_factor': 0.85,   # Minimum volume (85% of original)
        'max_factor': 1.15,   # Maximum volume (115% of original)
        'num_points': 7       # Number of volume points
    }),
    'metadata': {
        'label': 'silicon_eos',
        'description': 'Birch-Murnaghan EOS for silicon crystal'
    }
}

# Submit the workflow
wf_node = submit(BirchMurnaghanWorkChain, **inputs)
print(f"Submitted Birch-Murnaghan workflow: PK={wf_node.pk}")
```

### Advanced Configuration

#### Custom Volume Points

Instead of automatic volume generation, specify exact volumes:

```python
# Custom volume points
custom_volumes = [180.0, 190.0, 200.0, 210.0, 220.0, 230.0, 240.0]  # Ų

inputs['volume_points'] = orm.List(list=custom_volumes)
# Remove volume_range when using volume_points
del inputs['volume_range']
```

#### Convergence Settings

Control optimization convergence:

```python
inputs['optimization_settings'] = orm.Dict(dict={
    'force_tolerance': 0.01,     # Force convergence (eV/Å)
    'energy_tolerance': 1e-5,    # Energy convergence (eV)
    'max_iterations': 200,       # Maximum optimization steps
})
```

#### K-point Settings

Specify k-point sampling:

```python
from aiida.plugins import DataFactory

KpointsData = DataFactory('kpoints')
kpoints = KpointsData()
kpoints.set_kpoints_mesh([4, 4, 4], offset=[0.0, 0.0, 0.0])
kpoints.store()

inputs['kpoints'] = kpoints
```

### Monitoring the Workflow

Track workflow progress:

```bash
# Check overall status
verdi process status <workflow_PK>

# Monitor in real-time
verdi process watch <workflow_PK>

# View the workflow tree
verdi process tree <workflow_PK>

# Get detailed report
verdi process report <workflow_PK>
```

### Analyzing Results

Access the fitted equation of state:

```python
# Load completed workflow
wf = orm.load_node(wf_node.pk)

if wf.is_finished_ok:
    # Get the fitted parameters
    eos_results = wf.outputs.eos_parameters.get_dict()
    
    print("Equation of State Results:")
    print(f"Equilibrium volume: {eos_results['V0']:.2f} Ų")
    print(f"Bulk modulus: {eos_results['B0']:.2f} GPa")
    print(f"Pressure derivative: {eos_results['B0_prime']:.2f}")
    print(f"Ground state energy: {eos_results['E0']:.4f} eV")
    
    # Access individual calculations
    volume_calcs = wf.outputs.volume_calculations
    print(f"\nCompleted {len(volume_calcs)} volume calculations")
    
    # Get volume-energy data
    volumes = []
    energies = []
    
    for calc in volume_calcs:
        if calc.is_finished_ok:
            volume = calc.inputs.structure.get_cell_volume()
            energy = calc.outputs.output_parameters.get_dict()['total_energy']
            volumes.append(volume)
            energies.append(energy)
    
    # Plot results
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Sort by volume
    sorted_data = sorted(zip(volumes, energies))
    volumes, energies = zip(*sorted_data)
    
    plt.figure(figsize=(10, 6))
    plt.plot(volumes, energies, 'bo-', label='Calculated points')
    
    # Plot fitted curve
    V_fit = np.linspace(min(volumes), max(volumes), 100)
    E_fit = birch_murnaghan(V_fit, eos_results['E0'], eos_results['V0'], 
                           eos_results['B0'], eos_results['B0_prime'])
    plt.plot(V_fit, E_fit, 'r-', label='Birch-Murnaghan fit')
    
    plt.xlabel('Volume (Ų)')
    plt.ylabel('Energy (eV)')
    plt.title('Equation of State')
    plt.legend()
    plt.grid(True)
    plt.show()
```

## Transport Workflows (Planned)

Future transport workflows will include:

### I-V Curve Workflow

```python
# Planned implementation
IVCurveWorkChain = WorkflowFactory('fireball.iv_curve')

inputs = {
    'code': code,
    'structure': junction_structure,
    'fdata_remote': fdata_remote,
    'voltage_range': orm.Dict(dict={
        'min_voltage': -2.0,    # V
        'max_voltage': 2.0,     # V
        'num_points': 21
    }),
    'transport_base_parameters': transport_settings,
    'metadata': {'label': 'benzene_iv_curve'}
}

wf_node = submit(IVCurveWorkChain, **inputs)
```

### Transmission Spectrum Workflow

```python
# Planned implementation  
TransmissionWorkChain = WorkflowFactory('fireball.transmission_spectrum')

inputs = {
    'code': code,
    'structure': junction_structure,
    'fdata_remote': fdata_remote,
    'energy_range': orm.Dict(dict={
        'min_energy': -3.0,     # eV
        'max_energy': 3.0,      # eV
        'energy_resolution': 0.01  # eV
    }),
    'bias_voltages': orm.List(list=[0.0, 0.5, 1.0, 1.5]),
    'metadata': {'label': 'transmission_spectrum'}
}
```

## Custom Workflows

### Creating Simple Workflows

You can create custom workflows using AiiDA's WorkChain framework:

```python
from aiida.engine import WorkChain, ToContext, calcfunction
from aiida.plugins import CalculationFactory
from aiida import orm

@calcfunction
def scale_structure(structure, scale_factor):
    """Scale a structure by a given factor."""
    scaled_structure = structure.clone()
    scaled_structure.set_cell([
        [cell[0] * scale_factor, cell[1], cell[2]]
        for cell in structure.cell
    ])
    return scaled_structure

class StrainWorkChain(WorkChain):
    """Apply strain and calculate properties."""
    
    @classmethod
    def define(cls, spec):
        super().define(spec)
        
        # Inputs
        spec.input('code', valid_type=orm.Code)
        spec.input('structure', valid_type=orm.StructureData)
        spec.input('fdata_remote', valid_type=orm.RemoteData)
        spec.input('parameters', valid_type=orm.Dict)
        spec.input('strain_values', valid_type=orm.List)
        
        # Outputs
        spec.output('strain_energies', valid_type=orm.Dict)
        
        # Process outline
        spec.outline(
            cls.setup,
            cls.run_strain_calculations,
            cls.collect_results
        )
    
    def setup(self):
        """Initialize the workflow."""
        self.ctx.strain_calcs = {}
        
    def run_strain_calculations(self):
        """Submit calculations for each strain value."""
        FireballCalculation = CalculationFactory('fireball')
        
        for strain in self.inputs.strain_values:
            # Scale structure
            scaled_structure = scale_structure(
                self.inputs.structure, 
                orm.Float(1.0 + strain)
            )
            
            # Set up calculation inputs
            inputs = {
                'code': self.inputs.code,
                'structure': scaled_structure,
                'parameters': self.inputs.parameters,
                'fdata_remote': self.inputs.fdata_remote,
                'metadata': {
                    'label': f'strain_{strain:.3f}',
                    'options': {
                        'resources': {'num_machines': 1},
                        'max_wallclock_seconds': 1800,
                    }
                }
            }
            
            # Submit calculation
            calc = self.submit(FireballCalculation, **inputs)
            self.ctx.strain_calcs[strain] = calc
        
        # Wait for all calculations to complete
        return ToContext(**{
            f'calc_{i}': calc 
            for i, calc in enumerate(self.ctx.strain_calcs.values())
        })
    
    def collect_results(self):
        """Collect energies from all strain calculations."""
        strain_energies = {}
        
        for strain, calc in self.ctx.strain_calcs.items():
            if calc.is_finished_ok:
                energy = calc.outputs.output_parameters.get_dict()['total_energy']
                strain_energies[strain] = energy
        
        self.out('strain_energies', orm.Dict(dict=strain_energies))

# Usage
strain_values = [-0.02, -0.01, 0.0, 0.01, 0.02]  # ±2% strain

inputs = {
    'code': code,
    'structure': structure,
    'fdata_remote': fdata_remote,
    'parameters': parameters,
    'strain_values': orm.List(list=strain_values),
    'metadata': {'label': 'strain_analysis'}
}

wf_node = submit(StrainWorkChain, **inputs)
```

### Workflow Error Handling

Implement robust error handling:

```python
from aiida.engine import if_, while_

class RobustOptimizationWorkChain(WorkChain):
    """Optimization with automatic restart on failure."""
    
    @classmethod  
    def define(cls, spec):
        super().define(spec)
        
        spec.input('code', valid_type=orm.Code)
        spec.input('structure', valid_type=orm.StructureData)
        # ... other inputs
        
        spec.outline(
            cls.setup,
            while_(cls.should_continue)(
                cls.run_optimization,
                cls.inspect_optimization,
                if_(cls.optimization_failed)(
                    cls.handle_failure
                )
            ),
            cls.finalize
        )
        
        # Exit codes
        spec.exit_code(400, 'ERROR_MAX_RESTARTS', 
                      'Maximum number of restarts exceeded')
    
    def setup(self):
        """Initialize workflow."""
        self.ctx.restart_count = 0
        self.ctx.max_restarts = 3
        self.ctx.optimization_finished = False
    
    def should_continue(self):
        """Check if workflow should continue."""
        return (not self.ctx.optimization_finished and 
                self.ctx.restart_count < self.ctx.max_restarts)
    
    def run_optimization(self):
        """Submit optimization calculation."""
        # ... submit calculation
        return ToContext(opt_calc=calc)
    
    def inspect_optimization(self):
        """Check optimization results."""
        calc = self.ctx.opt_calc
        
        if calc.is_finished_ok:
            # Check convergence
            results = calc.outputs.output_parameters.get_dict()
            if results.get('optimization_converged', False):
                self.ctx.optimization_finished = True
                self.ctx.final_structure = calc.outputs.output_structure
        
    def optimization_failed(self):
        """Check if optimization failed."""
        return not self.ctx.optimization_finished
    
    def handle_failure(self):
        """Handle failed optimization."""
        self.ctx.restart_count += 1
        
        # Modify parameters for restart
        if self.ctx.restart_count == 1:
            # Try smaller time step
            pass
        elif self.ctx.restart_count == 2:
            # Try different optimization method
            pass
    
    def finalize(self):
        """Finalize workflow."""
        if not self.ctx.optimization_finished:
            return self.exit_codes.ERROR_MAX_RESTARTS
        
        self.out('optimized_structure', self.ctx.final_structure)
```

## Workflow Best Practices

### 1. Input Validation

Always validate inputs in workflows:

```python
def setup(self):
    """Validate inputs and setup context."""
    # Check required parameters
    required_params = ['iimage', 'iquench']
    params = self.inputs.parameters.get_dict()
    
    for param in required_params:
        if param not in params.get('OPTION', {}):
            return self.exit_codes.ERROR_INVALID_INPUT
    
    # Validate structure
    if len(self.inputs.structure.sites) == 0:
        return self.exit_codes.ERROR_EMPTY_STRUCTURE
```

### 2. Resource Management

Optimize computational resources:

```python
def determine_resources(self, num_atoms):
    """Determine computational resources based on system size."""
    if num_atoms < 50:
        return {'num_machines': 1, 'num_mpiprocs_per_machine': 4}
    elif num_atoms < 200:
        return {'num_machines': 2, 'num_mpiprocs_per_machine': 8}
    else:
        return {'num_machines': 4, 'num_mpiprocs_per_machine': 16}
```

### 3. Progress Reporting

Provide informative progress reports:

```python
def report_progress(self):
    """Report workflow progress."""
    completed = len([c for c in self.ctx.calculations.values() 
                    if c.is_finished])
    total = len(self.ctx.calculations)
    
    self.report(f"Progress: {completed}/{total} calculations completed")
    
    if completed == total:
        failed = len([c for c in self.ctx.calculations.values() 
                     if c.is_failed])
        if failed > 0:
            self.report(f"Warning: {failed} calculations failed")
```

## Next Steps

- {doc}`transport_tutorial`: Learn about transport calculations
- {doc}`../reference/index`: Detailed API documentation
- [AiiDA workflows documentation](https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/workflows/index.html)

For advanced workflow development, consult the AiiDA documentation on WorkChains and work functions.
