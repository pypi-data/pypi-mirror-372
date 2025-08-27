# AiiDA Fireball Plugin

```{image} _static/fireball_structure.png
:alt: Fireball Molecular Structure
:align: center
:width: 500px
:class: hero-image
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
:class-container: feature-grid

:::{grid-item-card} ⚡ Lightning Fast
:class-card: feature-card
:shadow: md

Semi-empirical DFT calculations orders of magnitude faster than traditional ab-initio methods while maintaining chemical accuracy.
:::

:::{grid-item-card} 🔬 Advanced Transport
:class-card: feature-card
:shadow: md

State-of-the-art quantum transport calculations with support for bias, interaction, and transmission properties.
:::

:::{grid-item-card} 🔄 Full Automation
:class-card: feature-card
:shadow: md

Automated workflows for equation of state, geometry optimization, and high-throughput screening studies.
:::

::::

## ✨ Key Features

::::{grid} 1 1 2 2
:gutter: 4
:class-container: features-section

:::{grid-item-card} 🎯 **Getting Started**
:link: user_guide/get_started
:link-type: doc
:class-card: getting-started-card
:shadow: lg

**Quick Setup in Minutes**

- One-command installation via pip
- Automated code configuration
- Interactive tutorials and examples

*Perfect for newcomers to AiiDA and Fireball*
:::

:::{grid-item-card} 🚀 **Transport Calculations**
:link: user_guide/transport_tutorial
:link-type: doc
:class-card: transport-card
:shadow: lg

**Advanced Quantum Transport**

- I-V curve calculations
- Transmission spectra analysis
- Multi-electrode configurations
- Bias-dependent transport

*Industry-grade transport property calculations*
:::

:::{grid-item-card} 📊 **Automated Workflows**
:link: user_guide/workflows
:link-type: doc
:class-card: workflows-card
:shadow: lg

**High-Throughput Ready**

- Birch-Murnaghan equation of state
- Bulk modulus extraction
- Parallel job management
- Error handling & restart

*Scale from single calculations to thousands*
:::

:::{grid-item-card} 🔧 **AiiDA Integration**
:link: reference/api
:link-type: doc
:class-card: integration-card
:shadow: lg

**Full Ecosystem Support**

- Complete provenance tracking
- Data management & querying
- REST API compatibility
- Plugin ecosystem integration

*Leverage the full power of AiiDA 2.0+*
:::

::::

## 🎯 Quick Start

Get up and running with AiiDA Fireball in just 3 steps:

::::{grid} 1 1 3 3
:gutter: 2

:::{grid-item-card} **1. Install**
:class-card: quick-start-card

```bash
pip install aiida-fireball
```
:::

:::{grid-item-card} **2. Configure**
:class-card: quick-start-card

```bash
verdi code setup fireball
```
:::

:::{grid-item-card} **3. Calculate**
:class-card: quick-start-card

```python
from aiida_fireball import FireballCalculation
result = FireballCalculation.run(...)
```
:::

::::

---

## 📖 Documentation Structure

```{toctree}
:maxdepth: 2
:caption: User Guide

user_guide/installation
user_guide/get_started
user_guide/transport_tutorial
user_guide/advanced_parallel
user_guide/workflows
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/index
```

## 🌟 Why Choose AiiDA Fireball?

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} **Performance**
:class-card: why-card

• **10-100x faster** than DFT
• Scales to thousands of atoms
• Optimized for HPC clusters
:::

:::{grid-item-card} **Accuracy**
:class-card: why-card

• Chemical accuracy for organic systems
• Validated against experiments
• Reliable transport properties
:::

:::{grid-item-card} **Productivity**
:class-card: why-card

• Automated workflows
• Error handling & restarts
• Full provenance tracking
:::

:::{grid-item-card} **Integration**
:class-card: why-card

• Native AiiDA 2.0+ support
• Python API & REST interface
• Extensible plugin architecture
:::

::::

## 🎓 Citation

If you use AiiDA Fireball in your research, please cite:

```bibtex
@software{aiida_fireball,
  title = {AiiDA Fireball Plugin},
  author = {Mohamed Mamlouk},
  url = {https://github.com/mohamedmamlouk/aiida-fireball},
  year = {2025}
}
```

Also consider citing [AiiDA](https://aiida.readthedocs.io/projects/aiida-core/en/latest/intro/citing.html) and [Fireball DFT](https://fireball-qmd.github.io/fireball.html).

---

## 🤝 Community & Support

::::{grid} 1 1 2 4
:gutter: 2

:::{grid-item-card} 📖 **Documentation**
:link: https://aiida-fireball.readthedocs.io
:class-card: support-card

Complete guides and API reference
:::

:::{grid-item-card} 🐛 **Issues**
:link: https://github.com/mohamedmamlouk/aiida-fireball/issues
:class-card: support-card

Report bugs and request features
:::

:::{grid-item-card} 💬 **Discussions**
:link: https://aiida.discourse.group
:class-card: support-card

Join the AiiDA community
:::

:::{grid-item-card} 📧 **Contact**
:link: mailto:contact@aiida-fireball.org
:class-card: support-card

Direct support and collaboration
:::

::::

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/mohamedmamlouk/aiida-fireball/blob/main/LICENSE) file for details.

---

{ref}`search`
