# AiiDA Fireball Plugin

Welcome to the AiiDA Fireball plugin documentation!

## Quick Start

The AiiDA Fireball plugin enables seamless integration of Fireball semi-empirical DFT calculations with the AiiDA workflow management framework.

### Features

- Complete Fireball integration
- Transport property calculations  
- Automated workflows
- Full provenance tracking

### Installation

```bash
pip install aiida-fireball
```

### Basic Usage

```python
from aiida import orm
from aiida.plugins import CalculationFactory
from aiida.engine import submit

FireballCalculation = CalculationFactory('fireball')

inputs = {
    'code': orm.load_code('fireball@localhost'),
    'structure': structure,
    'parameters': parameters,
    'kpoints': kpoints,
    'fdata_remote': fdata_remote,
}

calc_node = submit(FireballCalculation, **inputs)
```

## Documentation

```{toctree}
:maxdepth: 2

user_guide/installation
user_guide/get_started
user_guide/transport_tutorial
user_guide/workflows
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/index
```
```

## Support

- GitHub: [mohamedmamlouk/aiida-fireball](https://github.com/mohamedmamlouk/aiida-fireball)
- Issues: [GitHub Issues](https://github.com/mohamedmamlouk/aiida-fireball/issues)

## License

MIT License - see [LICENSE](https://github.com/mohamedmamlouk/aiida-fireball/blob/main/LICENSE)
