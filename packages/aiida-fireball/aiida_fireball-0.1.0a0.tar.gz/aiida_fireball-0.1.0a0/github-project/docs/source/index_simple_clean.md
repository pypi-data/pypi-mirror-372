# AiiDA Fireball Plugin

```{image} _static/download.jpeg
:alt: AiiDA Fireball Quantum Simulation
:align: center
:width: 600px
```

<div align="center">

**High-Performance Semi-Empirical DFT Calculations with Advanced Transport Properties**

[![PyPI version](https://img.shields.io/pypi/v/aiida-fireball.svg)](https://pypi.org/project/aiida-fireball/)
[![Python versions](https://img.shields.io/pypi/pyversions/aiida-fireball.svg)](https://pypi.org/project/aiida-fireball/)
[![Documentation Status](https://readthedocs.org/projects/aiida-fireball/badge/?version=latest)](https://aiida-fireball.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/mohamedmamlouk/aiida-fireball.svg)](https://github.com/mohamedmamlouk/aiida-fireball/blob/main/LICENSE)

</div>

---

## 🚀 What is AiiDA Fireball?

AiiDA Fireball is a cutting-edge plugin that seamlessly integrates the **Fireball semi-empirical DFT code** with the **AiiDA computational workflow management platform**. Designed for researchers who need efficient, scalable, and reproducible quantum mechanical calculations.

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} ⚡ Fast DFT Calculations
High-performance semi-empirical density functional theory calculations with optimized algorithms.
:::

:::{grid-item-card} 🌊 Transport Properties  
Advanced electronic transport property calculations with flexible optional files.
:::

:::{grid-item-card} 🔬 Workflow Automation
Automated equation of state calculations and parameter optimization workflows.
:::

:::{grid-item-card} 📊 Data Provenance
Full provenance tracking and workflow reproducibility for all calculations.
:::

:::{grid-item-card} 🚀 High-Throughput
Designed for large-scale computational studies with parallel execution.
:::

:::{grid-item-card} 🔧 Easy Integration
Seamless integration with existing AiiDA workflows and databases.
:::

::::

---

## 📋 Key Features

- **Complete Fireball Integration**: Full support for all Fireball calculation types
- **Advanced Transport Calculations**: State-of-the-art transport property calculations
- **Flexible Input Management**: Support for optional files and complex input structures  
- **Automated Workflows**: Built-in WorkChains for common calculation patterns
- **Result Parsing**: Comprehensive parsing of output files and properties
- **Error Handling**: Robust error detection and recovery mechanisms
- **Documentation**: Extensive documentation with examples and tutorials

---

## 🎯 Main Components

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} 🚀 Getting Started
:link: user_guide/get_started
:link-type: doc

Quick setup and your first calculations
^^^
- Installation guide
- Basic configuration  
- Your first DFT run
- Example workflows

+++
Learn the basics →
:::

:::{grid-item-card} 🌊 Transport Calculations
:link: user_guide/tutorial
:link-type: doc

Advanced transport property analysis
^^^
- Energy-dependent scanning
- Optional file management
- Result visualization
- Performance optimization

+++
Explore transport →
:::

:::{grid-item-card} 🔧 Developer Guide
:link: developer_guide/index
:link-type: doc

Extend and customize the plugin
^^^
- Plugin architecture
- Adding new parsers
- Custom workflows
- Contributing guidelines

+++
Start developing →
:::

::::

---

## 🚀 Quick Start

### Installation

```bash
pip install aiida-fireball
```

### Basic Usage

```python
from aiida_fireball import FireballCalculation
from aiida import load_profile, submit

# Load your AiiDA profile
load_profile()

# Create a calculation
calc = FireballCalculation()

# Set up your inputs (structure, parameters, etc.)
# ... (see user guide for details)

# Submit calculation
result = submit(calc)
```

### Transport Calculations

```python
from aiida_fireball.workflows import TransportScanWorkChain

# Create transport workflow
workflow = TransportScanWorkChain()

# Configure energy scanning
inputs = {
    'energy_range': {'start': -2.0, 'end': 1.0, 'step': 0.1},
    'fireball_inputs': {...}
}

# Submit workflow
result = submit(workflow, inputs)
```

---

## 📚 Documentation Structure

```{toctree}
:maxdepth: 2
:hidden:

user_guide/index
developer_guide/index
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/mohamedmamlouk/aiida-fireball/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/mohamedmamlouk/aiida-fireball/blob/main/LICENSE) file for details.

## 🙏 Acknowledgements

- The AiiDA team for providing an excellent workflow management platform
- The Fireball development team for the semi-empirical DFT code
- All contributors and users of this plugin
