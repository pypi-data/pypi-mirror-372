Tutorial
========

This tutorial will guide you through using AiiDA Fireball for various types of calculations.

Basic Single Point Calculation
-------------------------------

Let's start with a simple single point energy calculation for a water molecule.

Setting up the Structure
~~~~~~~~~~~~~~~~~~~~~~~~~

First, create the molecular structure::

    from aiida import orm
    
    # Create water molecule structure
    structure = orm.StructureData()
    structure.append_atom(position=(0.0, 0.0, 0.0), symbols='O')
    structure.append_atom(position=(0.757, 0.587, 0.0), symbols='H') 
    structure.append_atom(position=(-0.757, 0.587, 0.0), symbols='H')
    
    # Set a large unit cell to avoid periodic interactions
    structure.set_cell([10.0, 10.0, 10.0])
    structure.set_pbc([False, False, False])  # No periodic boundary conditions

Configuring Parameters
~~~~~~~~~~~~~~~~~~~~~~

Set up the calculation parameters::

    parameters = orm.Dict(dict={
        'max_scf_iterations': 100,
        'scf_tolerance': 1e-6,
        'charge': 0,
        'spin': 1,
        'temperature': 300.0  # Kelvin
    })

Running the Calculation
~~~~~~~~~~~~~~~~~~~~~~~

Submit the calculation::

    from aiida.engine import submit
    from aiida_fireball import FireballCalculation
    
    builder = FireballCalculation.get_builder()
    builder.structure = structure
    builder.parameters = parameters 
    builder.code = orm.load_code('fireball@localhost')
    
    calc = submit(builder)
    print(f"Calculation PK: {calc.pk}")

Transport Calculations
----------------------

AiiDA Fireball supports advanced transport property calculations.

Simple Transport Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a single transport calculation::

    # Additional parameters for transport
    transport_params = orm.Dict(dict={
        'max_scf_iterations': 100,
        'scf_tolerance': 1e-6,
        'transport': True,
        'energy': -1.0  # Fermi energy offset in eV
    })
    
    builder = FireballCalculation.get_builder()
    builder.structure = structure
    builder.parameters = transport_params
    builder.code = orm.load_code('fireball@localhost')
    
    calc = submit(builder)

Transport Energy Scanning
~~~~~~~~~~~~~~~~~~~~~~~~~

For systematic transport property scanning across different energies::

    from aiida_fireball.workflows import TransportScanWorkChain
    
    # Setup the workflow
    builder = TransportScanWorkChain.get_builder()
    builder.fireball_code = orm.load_code('fireball@localhost')
    builder.structure = structure
    
    # Base parameters
    builder.parameters = orm.Dict(dict={
        'max_scf_iterations': 100,
        'scf_tolerance': 1e-6,
        'transport': True
    })
    
    # Energy range for scanning
    builder.energy_range = orm.Dict(dict={
        'start': -2.0,  # Starting energy (eV)
        'end': 1.0,     # Ending energy (eV)
        'step': 0.1     # Energy step (eV)
    })
    
    # Submit the workflow
    workflow = submit(builder)
    print(f"Transport workflow PK: {workflow.pk}")

Working with Results
--------------------

Accessing Calculation Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After a calculation completes::

    from aiida import orm
    
    # Load the calculation
    calc = orm.load_node(CALC_PK)  # Replace with your PK
    
    # Check if successful
    if calc.is_finished_ok:
        # Get the results
        results = calc.outputs.output_parameters.get_dict()
        
        print("Calculation Results:")
        print(f"Total Energy: {results.get('total_energy')} eV")
        print(f"SCF Converged: {results.get('scf_converged')}")
        print(f"SCF Iterations: {results.get('scf_iterations')}")
        
        # Additional properties if available
        if 'forces' in results:
            print(f"Max Force: {max(results['forces'])} eV/Å")
            
    else:
        print("Calculation failed or still running")
        if calc.is_excepted:
            print(f"Exception: {calc.exception}")

Analyzing Transport Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For transport calculations::

    # Transport-specific results
    if 'transport_properties' in calc.outputs:
        transport = calc.outputs.transport_properties.get_dict()
        
        print("Transport Properties:")
        print(f"Conductance: {transport.get('conductance')} e²/h")
        print(f"Transmission: {transport.get('transmission')}")

Working with Workflows
~~~~~~~~~~~~~~~~~~~~~~

For workflow results::

    # Load the workflow
    workflow = orm.load_node(WORKFLOW_PK)
    
    if workflow.is_finished_ok:
        # Get all sub-calculations
        calculations = workflow.called
        
        print(f"Workflow completed with {len(calculations)} calculations")
        
        # Analyze each calculation
        for calc in calculations:
            if calc.is_finished_ok:
                results = calc.outputs.output_parameters.get_dict()
                energy = results.get('energy_fermi_offset', 'N/A')
                conductance = results.get('conductance', 'N/A')
                print(f"Energy: {energy} eV, Conductance: {conductance}")

Advanced Topics
---------------

Custom Input Files
~~~~~~~~~~~~~~~~~~

AiiDA Fireball supports custom optional files like ``trans.optional``::

    # Create custom optional file content
    optional_content = """
    # Custom transport parameters
    energy_window = 5.0
    kpoints = 10 10 1
    """
    
    optional_file = orm.SinglefileData.from_string(
        optional_content, 
        filename='trans.optional'
    )
    
    # Add to calculation
    builder.optional_files = {'trans.optional': optional_file}

Error Handling
~~~~~~~~~~~~~~

Check for common issues::

    calc = orm.load_node(CALC_PK)
    
    if calc.is_excepted:
        print(f"Calculation failed with exception: {calc.exception}")
    elif calc.is_killed:
        print("Calculation was killed")
    elif not calc.is_finished:
        print(f"Calculation still running, state: {calc.process_state}")
    else:
        # Check for warnings in outputs
        if 'warnings' in calc.outputs.output_parameters.get_dict():
            warnings = calc.outputs.output_parameters.get_dict()['warnings']
            print(f"Calculation completed with warnings: {warnings}")

Best Practices
--------------

1. **Structure Validation**: Always validate your structures before submission
2. **Parameter Testing**: Start with loose convergence criteria, then tighten
3. **Resource Management**: Use appropriate computational resources
4. **Provenance**: Keep track of calculation dependencies
5. **Batch Processing**: Use workflows for systematic studies

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Calculation fails immediately:**

- Check that Fireball is properly installed on the computer
- Verify the code path is correct
- Ensure the structure is valid

**SCF not converging:**

- Increase ``max_scf_iterations``
- Adjust ``scf_tolerance``
- Try different mixing parameters

**Transport calculations failing:**

- Verify the structure is suitable for transport (e.g., proper leads)
- Check energy range is reasonable
- Ensure transport-specific files are properly formatted

Getting Help
~~~~~~~~~~~~

- Check the calculation logs: ``verdi calcjob gotocomputer CALC_PK``
- View the input files: ``verdi calcjob inputls CALC_PK``
- Examine output files: ``verdi calcjob outputls CALC_PK``
- Join the AiiDA community: https://aiida.discourse.group/
