🐐 ggoat: Grammar of Graphics for Python
=========================================

.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/ggoat/ggoat/blob/main/LICENSE
   :alt: License

Welcome to **ggoat** - a clean, lightweight implementation of ggplot2's Grammar of Graphics for Python, optimized for Pyodide and browser environments.

🌟 Key Features
---------------

* **🔗 Method chaining**: Fluent, readable syntax
* **📦 Minimal imports**: Just ``ggplot`` and ``aes``
* **🌐 Browser-ready**: Works in Pyodide, Jupyter, and Python
* **⚡ Lightweight**: Minimal dependencies
* **🎨 Rich visualizations**: Support for all major plot types
* **🔧 Extensible**: Easy to customize and extend

🚀 Quick Start
--------------

Install ggoat (when available)::

    pip install ggoat

Create your first plot::

    from ggoat import ggplot, aes
    
    data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]}
    
    plot = (ggplot(data, aes(x='x', y='y'))
            .geom_point(size=3, color='steelblue')
            .labs(title="My First ggoat Plot"))
    
    plot.show()

📚 Documentation
----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   
   installation
   getting_started
   gallery
   tutorials/index
   api/index

.. toctree::
   :maxdepth: 2
   :caption: Examples
   
   examples/basic_plots
   examples/advanced_plots
   examples/jupyter_integration
   examples/pyodide_deployment

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/core
   api/aesthetics
   api/geoms
   api/scales
   api/themes
   api/facets
   api/coordinates

.. toctree::
   :maxdepth: 1
   :caption: Development
   
   contributing
   changelog
   license

🎯 Why ggoat?
-------------

**Clean API**: Method chaining provides a fluent, readable interface::

    # Traditional ggplot2 (R-style)
    ggplot(data, aes(x='x', y='y')) + geom_point() + labs(title='Plot')
    
    # ggoat (method chaining)
    ggplot(data, aes(x='x', y='y')).geom_point().labs(title='Plot')

**Browser Optimized**: Designed for modern web environments:

* Works seamlessly in Pyodide and WebAssembly
* Minimal dependencies for fast loading
* Integrates with lets-plot JavaScript rendering
* Export capabilities for web deployment

**Easy to Use**: Simple imports and intuitive syntax::

    from ggoat import ggplot, aes  # Only two imports needed!

🔬 Grammar of Graphics
---------------------

ggoat implements Leland Wilkinson's Grammar of Graphics, which decomposes plots into:

**Data**: Your dataset (dict or DataFrame)::

    data = {'x': [1, 2, 3], 'y': [4, 5, 6], 'group': ['A', 'B', 'A']}

**Aesthetics**: How data maps to visual properties::

    aes(x='x', y='y', color='group', size='importance')

**Geometries**: Visual representations of data::

    .geom_point()   # Scatter plot
    .geom_line()    # Line plot
    .geom_bar()     # Bar chart

**Scales**: How aesthetics are displayed::

    .scale_color_manual(['red', 'blue', 'green'])

**Coordinates**: The coordinate system::

    .coord_cartesian(xlim=(0, 10))

**Facets**: Small multiples::

    .facet_wrap('category')

**Themes**: Overall visual styling::

    .theme_minimal()

📊 Supported Plot Types
-----------------------

ggoat supports all major visualization types:

* **Points**: Scatter plots, bubble charts
* **Lines**: Time series, trend lines
* **Bars**: Bar charts, histograms
* **Areas**: Area plots, stacked areas
* **Statistical**: Box plots, violin plots, density plots
* **Text**: Annotations, labels
* **Specialized**: Error bars, tiles, contours

🌐 Platform Support
-------------------

* **Jupyter Notebooks**: Full integration with IPython display
* **Pyodide**: Optimized for WebAssembly environments
* **Standard Python**: Works in any Python environment
* **Web Browsers**: Direct JavaScript rendering via lets-plot

📖 Learning Path
----------------

1. **Start Here**: :doc:`getting_started` - Basic concepts and first plots
2. **Tutorial**: :doc:`tutorials/index` - Step-by-step learning
3. **Examples**: :doc:`examples/basic_plots` - Copy-paste examples
4. **API Reference**: :doc:`api/index` - Complete function reference
5. **Advanced**: :doc:`examples/advanced_plots` - Complex visualizations

🤝 Contributing
---------------

We welcome contributions! See :doc:`contributing` for guidelines.

📄 License
----------

ggoat is released under the MIT License. See :doc:`license` for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`