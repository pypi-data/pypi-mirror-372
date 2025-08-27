# Installation Guide

This guide will walk you through installing the AiiDA Fireball plugin and setting up your computational environment.

## Prerequisites

Before installing AiiDA Fireball, ensure you have:

### System Requirements
- **Operating System**: Linux, macOS, or Windows (WSL recommended)
- **Python**: 3.8 or later
- **Memory**: At least 4 GB RAM (8 GB+ recommended)
- **Storage**: At least 10 GB free space

### Required Software

#### 1. AiiDA Core
AiiDA Fireball requires AiiDA 2.0 or later:

```bash
pip install aiida-core[atomic_tools]>=2.0.0
```

#### 2. PostgreSQL Database
AiiDA requires a PostgreSQL database:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
```

#### 3. RabbitMQ Message Broker
For workflow management:

**Ubuntu/Debian:**
```bash
sudo apt install rabbitmq-server
```

**macOS:**
```bash
brew install rabbitmq
brew services start rabbitmq
```

**CentOS/RHEL:**
```bash
sudo yum install rabbitmq-server
sudo systemctl start rabbitmq-server
```

#### 4. Fireball Code
Download and compile the Fireball code:

```bash
# Download from the official Fireball website
wget https://fireball-dft.org/downloads/fireball-X.X.tar.gz
tar -xzf fireball-X.X.tar.gz
cd fireball-X.X

# Compile (adjust for your system)
make
```

## Installation Methods

### Method 1: Install from PyPI (Recommended)

Once available on PyPI:

```bash
pip install aiida-fireball
```

### Method 2: Install from Source

For the latest development version:

```bash
git clone https://github.com/yourusername/aiida-fireball.git
cd aiida-fireball
pip install -e .
```

### Method 3: Development Installation

For contributors and developers:

```bash
git clone https://github.com/yourusername/aiida-fireball.git
cd aiida-fireball
pip install -e .[dev]
pre-commit install
```

## Configuration

### 1. AiiDA Profile Setup

Create and configure an AiiDA profile:

```bash
verdi profile setup core.psql_dos
```

Follow the interactive prompts to configure:
- Database name and credentials
- Message broker settings
- User information

### 2. Start AiiDA Daemon

The daemon manages workflow execution:

```bash
verdi daemon start
```

Check daemon status:
```bash
verdi daemon status
```

### 3. Computer Configuration

Set up a computer for running calculations:

```bash
verdi computer setup
```

Example configuration for localhost:
- Label: `localhost`
- Hostname: `localhost`
- Transport: `local`
- Scheduler: `direct`
- Work directory: `/tmp/aiida_work`

Configure the computer:
```bash
verdi computer configure local localhost
```

Test the connection:
```bash
verdi computer test localhost
```

### 4. Code Setup

Register your Fireball executable:

```bash
verdi code setup
```

Configuration parameters:
- Label: `fireball-v3.0`
- Description: `Fireball semi-empirical DFT code`
- Default input plugin: `fireball`
- Remote computer: `localhost`
- Remote absolute path: `/path/to/fireball.x`

Alternatively, create via Python:

```python
from aiida import orm

# Load computer
computer = orm.load_computer('localhost')

# Create code
code = orm.Code(
    input_plugin_name='fireball',
    remote_computer_exec=[computer, '/path/to/fireball.x']
)
code.label = 'fireball-v3.0'
code.description = 'Fireball semi-empirical DFT code v3.0'
code.store()
```

## Verification

### 1. Plugin Installation

Verify the plugin is correctly installed:

```bash
verdi plugin list aiida.calculations
```

You should see `fireball` in the output.

### 2. Import Test

Test importing the plugin in Python:

```python
from aiida.plugins import CalculationFactory

# This should work without errors
FireballCalculation = CalculationFactory('fireball')
print("AiiDA Fireball plugin successfully imported!")
```

### 3. Run Test Calculation

Run a simple test to ensure everything works:

```python
from aiida import orm
from aiida.plugins import CalculationFactory, DataFactory
from aiida.engine import run_get_node

# Load plugins
FireballCalculation = CalculationFactory('fireball')
StructureData = DataFactory('structure')

# Create simple structure
structure = StructureData()
structure.set_cell([[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]])
structure.append_atom(position=[0.0, 0.0, 0.0], symbols='H')
structure.append_atom(position=[0.74, 0.0, 0.0], symbols='H')

# Load code
code = orm.load_code('fireball-v3.0@localhost')

# Set up inputs
inputs = {
    'code': code,
    'structure': structure,
    'metadata': {
        'options': {
            'resources': {'num_machines': 1},
            'max_wallclock_seconds': 300,
        }
    }
}

# Run calculation (for testing only - use submit for production)
result, node = run_get_node(FireballCalculation, **inputs)
print(f"Test calculation completed with PK={node.pk}")
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart if needed
sudo systemctl restart postgresql
```

#### 2. RabbitMQ Issues
```bash
# Check RabbitMQ status
sudo systemctl status rabbitmq-server

# Reset if needed
sudo rabbitmqctl stop_app
sudo rabbitmqctl reset
sudo rabbitmqctl start_app
```

#### 3. Plugin Not Found
If `verdi plugin list` doesn't show the fireball plugin:

```bash
# Reinstall the plugin
pip uninstall aiida-fireball
pip install aiida-fireball

# Clear AiiDA cache
verdi calcjob cleanworkdir -f
```

#### 4. Permission Issues
Ensure proper permissions for work directories:

```bash
chmod 755 /tmp/aiida_work
chown -R $USER:$USER /tmp/aiida_work
```

### Getting Help

If you encounter issues:

1. Check the [FAQ](faq.md)
2. Search [GitHub Issues](https://github.com/yourusername/aiida-fireball/issues)
3. Ask on [AiiDA Discourse](https://aiida.discourse.group/)
4. Create a new [GitHub Issue](https://github.com/yourusername/aiida-fireball/issues/new)

## Next Steps

With AiiDA Fireball installed and configured:

1. Follow the [First Calculation Tutorial](first_calculation.md)
2. Explore [Transport Calculations](transport_tutorial.md)
3. Check out the [Examples](../examples/README.md)
4. Read the [API Reference](../reference/api.md)
