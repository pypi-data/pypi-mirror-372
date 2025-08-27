# ggoat

**Grammar of Graphics for Python - optimized for Pyodide and browser environments**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://ggoat.readthedocs.io/)

ggoat is a clean, lightweight implementation of ggplot2's Grammar of Graphics for Python based on [Lets-Plot](https://lets-plot.org/) JavaScript API. Why Lets-Plot offers a powerful experience, ggoat aims at being more Pythonic, working in modern web environments including Marimo, Jupyter, and Pyodide-based Python platforms.

## Features

- **Method chaining**: Fluent, readable syntax instead of `+` operator
- **Minimal imports**: Just `ggplot` and `aes` - that's it!
- **Browser-ready**: Optimized for Pyodide and WebAssembly environments
- **Lightweight**: Zero heavy dependencies, works with Python stdlib
- **Rich visualizations**: Support for all major plot types and customizations
- **Extensible**: Easy to customize themes, scales, and coordinate systems

## Quick Start

```python
from ggoat import ggplot, aes

# Your data (works with dicts or pandas DataFrames)
data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10], 'group': ['A', 'A', 'B', 'B', 'C']}

# Create beautiful plots with method chaining
plot = (
    ggplot(data, aes(x='x', y='y', color='group'))
    .geom_point(size=3, alpha=0.7)
    .geom_line(size=1)
    .labs(title="My Beautiful Plot", x="X Values", y="Y Values")
    .theme_minimal()
)

plot.show()
```

## Documentation

**[Complete Documentation](https://ggoat.readthedocs.io/)**

- **[Getting Started](docs/getting_started.rst)** - Your first plots in minutes
- **[API Reference](docs/api/)** - Complete function documentation  
- **[Examples Gallery](docs/examples/)** - Copy-paste examples
- **[Jupyter Tutorials](examples/)** - Interactive notebooks

## Installation

```bash
# Basic installation (when available)
pip install ggoat

# micropip installation
micropip install ggoat

# Development installation
git clone https://github.com/ggoat/ggoat.git
cd ggoat
pip install -e .
```

## Contributing

I welcome contributions! The codebase includes comprehensive documentation and examples.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Thanks

- JetBrains develops Lets-Plot, a powerful JavaScript-based plotting library for Python and Kotlin.
- The grammar of graphics used by Lets-Plot and many other projects like Plotnine, is based on the one developped for ggplot2, a world-class data visualization package for the R statistical language.
- Pyodide is a wonderful way fo getting started with Python data science Python. Just [open a Marimo notebook](https://marimo.new/) (based on Pyodide), and you can start your journey in being the smart ass in the room.

---

Happy plotting with ggoat! 🐐