# AiiDA Fireball Plugin

![AiiDA Fireball](_static/download.jpeg)

Welcome to the **AiiDA Fireball Plugin** - a comprehensive integration of the Fireball semi-empirical DFT code with the AiiDA computational workflow management platform.

## What is AiiDA Fireball?

AiiDA Fireball is a plugin that enables seamless execution and management of Fireball calculations within the AiiDA ecosystem. It provides:

- **Full Fireball Integration**: Complete support for Fireball semi-empirical DFT calculations
- **Advanced Transport Calculations**: State-of-the-art transport property calculations with flexible optional files
- **Workflow Automation**: Automated equation of state calculations and parameter optimization
- **Provenance Tracking**: Full data provenance and workflow reproducibility
- **High-Throughput Capabilities**: Designed for large-scale computational studies
</div>
```

---

## ✨ Key Features

````{grid} 1 2 3 3
:gutter: 3
:margin: 3

```{grid-item-card} ⚡ Fast DFT Calculations
:class-card: feature-card
:class-header: text-center

High-performance semi-empirical density functional theory calculations with optimized algorithms and parallel processing.
```

```{grid-item-card} 🌊 Transport Properties  
:class-card: feature-card
:class-header: text-center

Automated scanning of electronic transport properties across energy ranges with intelligent workflow management.
```

```{grid-item-card} 🔬 Advanced Workflows
:class-card: feature-card
:class-header: text-center

Sophisticated WorkChains for complex multi-step calculations with built-in error handling and result analysis.
```

```{grid-item-card} 📊 Data Analysis
:class-card: feature-card
:class-header: text-center

Comprehensive parsing and visualization of calculation results with advanced analytics tools.
```

```{grid-item-card} 🚀 AiiDA Integration
:class-card: feature-card
:class-header: text-center

Seamless integration with the AiiDA ecosystem for scalable, reproducible, and FAIR computational workflows.
```

```{grid-item-card} 🔧 Easy Setup
:class-card: feature-card
:class-header: text-center

Simple installation and configuration process with automatic dependency resolution.
```
````

---

## 🎯 Main Components

````{grid} 1 1 3 3
:gutter: 3
:margin: 3

```{grid-item-card} 
:class-card: getting-started-card
:class-header: text-center

**🚀 Getting Started**
^^^
Quick setup and first calculations

- Installation guide
- Basic configuration  
- Your first DFT run
- Example workflows

+++
```python
pip install aiida-fireball
verdi quicksetup  # Ready to go!
```
```

```{grid-item-card}
:class-card: transport-card  
:class-header: text-center

**🌊 Transport Calculations**
^^^
Advanced transport property analysis

- Energy-dependent scanning
- Automated workflows
- Result visualization
- Performance optimization

+++
```python
from aiida_fireball.workflows import TransportScanWorkChain
# Automated transport scanning
```
```

```{grid-item-card}
:class-card: workflows-card
:class-header: text-center

**🔧 Workflows & Advanced Usage**
^^^
Complex calculation workflows

- WorkChain development
- Error handling strategies
- Result post-processing
- Best practices guide

+++
```python
from aiida import submit
submit(MyWorkChain, inputs)
```
```
````

---

## 🚀 Quick Start

```{raw} html
<div id="quick-start" style="margin: 3rem 0; padding: 2rem; background: #3a3a4e; border-radius: 15px; border: 2px solid #667eea;">
    <h2 style="text-align: center; color: #00d4ff; margin-bottom: 2rem;">⚡ Get Started in 3 Steps</h2>
</div>
```

### Step 1: Installation

```bash
# Install the plugin
pip install aiida-fireball

# Set up AiiDA
verdi quicksetup --profile fireball-lab
```

### Step 2: Configure Computer

```bash
# Set up your computer
verdi computer setup --transport local --scheduler direct quantum-computer
verdi computer configure local quantum-computer
```

### Step 3: Run Your First Calculation

```python
from aiida_fireball import FireballCalculation
from aiida import submit

# Create and submit calculation
calc = FireballCalculation()
result = submit(calc)
```

```{raw} html
<div style="text-align: center; margin: 2rem 0; padding: 1.5rem; background: #2a2a3e; border-radius: 10px; border: 1px solid #4a4a6e;">
    <h3 style="color: #00d4ff; margin-bottom: 1rem;">🎉 You're Ready!</h3>
    <p style="color: #e0e0e0;">Your AiiDA Fireball environment is now set up and ready for quantum simulations.</p>
    <div style="margin-top: 1.5rem;">
        <a href="user_guide/get_started.html" style="background: #667eea; color: white; padding: 10px 20px; border-radius: 20px; text-decoration: none; font-weight: 600; margin: 0 0.5rem;">📚 User Guide</a>
        <a href="user_guide/tutorial.html" style="background: #4facfe; color: white; padding: 10px 20px; border-radius: 20px; text-decoration: none; font-weight: 600; margin: 0 0.5rem;">🎯 Tutorial</a>
    </div>
</div>
```

---

```{toctree}
:maxdepth: 2
:hidden:

user_guide/index
developer_guide/index
```

```{raw} html
<div style="text-align: center; margin: 3rem 0; padding: 2rem; background: #2a2a3e; border-radius: 15px; border: 1px solid #4a4a6e;">
    <h2 style="color: #f093fb; margin-bottom: 1rem;">🌟 Join the Community</h2>
    <p style="color: #e0e0e0; margin-bottom: 1.5rem;">Connect with researchers and developers using AiiDA Fireball</p>
    <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
        <a href="https://github.com/mohamedmamlouk/aiida-fireball/issues" style="background: #3a3a4e; color: #e0e0e0; padding: 8px 16px; border-radius: 15px; text-decoration: none; border: 1px solid #4a4a6e;">💬 Issues</a>
        <a href="https://github.com/mohamedmamlouk/aiida-fireball/discussions" style="background: #3a3a4e; color: #e0e0e0; padding: 8px 16px; border-radius: 15px; text-decoration: none; border: 1px solid #4a4a6e;">🗨️ Discussions</a>
        <a href="https://github.com/mohamedmamlouk/aiida-fireball" style="background: #3a3a4e; color: #e0e0e0; padding: 8px 16px; border-radius: 15px; text-decoration: none; border: 1px solid #4a4a6e;">⭐ Star on GitHub</a>
    </div>
</div>
```
