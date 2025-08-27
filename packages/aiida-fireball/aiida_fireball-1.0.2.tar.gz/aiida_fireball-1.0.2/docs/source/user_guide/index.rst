User Guide
==========

Welcome to the AiiDA Fireball user guide. This section provides comprehensive documentation for users who want to run Fireball calculations using AiiDA.

.. toctree::
   :maxdepth: 2
   
   get_started

Overview
--------

AiiDA Fireball is a plugin that integrates the Fireball semi-empirical DFT code with the AiiDA workflow management platform. It provides:

- **Complete Fireball Integration**: Full support for all Fireball calculation types
- **Transport Calculations**: Advanced transport property calculations with energy scanning
- **Workflow Automation**: Automated parameter optimization and systematic studies  
- **Data Provenance**: Complete tracking of calculation history and dependencies
- **High-Throughput**: Designed for large-scale computational studies

Getting Started
---------------

New to AiiDA Fireball? Start with the :doc:`get_started` guide to learn how to install and configure the plugin.

Key Features
------------

Calculation Types
~~~~~~~~~~~~~~~~~

- Single point energy calculations
- Geometry optimizations
- Molecular dynamics simulations  
- Transport property calculations
- Band structure calculations
- Equation of state studies

Input Management  
~~~~~~~~~~~~~~~~

- Flexible parameter handling
- Optional file support (trans.optional, etc.)
- Automatic input validation
- Structure preprocessing and validation

Output Parsing
~~~~~~~~~~~~~~

- Energy and forces extraction
- Electronic properties parsing
- Transport coefficients calculation
- Comprehensive error detection and reporting

Workflow Integration
~~~~~~~~~~~~~~~~~~~~

- WorkChain support for complex multi-step workflows
- Automatic restart capabilities for failed calculations
- Intelligent error handling and recovery
- Built-in results analysis tools
