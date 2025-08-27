Getting Started
===============

Welcome to ggoat! This guide will get you creating beautiful plots in minutes.

Core Concepts
-------------

ggoat implements the **Grammar of Graphics**, which breaks plots into components:

1. **Data**: Your dataset
2. **Aesthetics**: How data maps to visual properties  
3. **Geometries**: Visual representations (points, lines, bars)
4. **Scales**: How aesthetics are displayed
5. **Coordinates**: The coordinate system
6. **Facets**: Small multiples
7. **Themes**: Overall visual styling

Your First Plot
---------------

Let's create a simple scatter plot::

    from ggoat import ggplot, aes
    
    # Sample data
    data = {
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'group': ['A', 'A', 'B', 'B', 'C']
    }
    
    # Create plot with method chaining
    plot = (ggplot(data, aes(x='x', y='y', color='group'))
            .geom_point(size=3)
            .labs(title="My First ggoat Plot"))
    
    # Display the plot
    plot.show()

Method Chaining
---------------

ggoat uses **method chaining** instead of the ``+`` operator::

    # Traditional ggplot2 (R-style)
    ggplot(data, aes(x='x', y='y')) + geom_point() + labs(title='Plot')
    
    # ggoat (method chaining)
    ggplot(data, aes(x='x', y='y')).geom_point().labs(title='Plot')

This makes code more readable and Python-friendly.

Basic Plot Types
----------------

**Scatter Plot**::

    ggplot(data, aes(x='x', y='y')).geom_point()

**Line Plot**::

    ggplot(data, aes(x='x', y='y')).geom_line()

**Bar Chart**::

    ggplot(data, aes(x='category', y='value')).geom_bar(stat='identity')

**Histogram**::

    ggplot(data, aes(x='values')).geom_histogram(bins=20)

**Box Plot**::

    ggplot(data, aes(x='group', y='values')).geom_boxplot()

Working with Data
-----------------

ggoat accepts Python dictionaries and pandas DataFrames:

**Dictionary Data**::

    data = {
        'x': [1, 2, 3, 4],
        'y': [10, 20, 15, 25],
        'category': ['A', 'B', 'A', 'B']
    }

**DataFrame Data** (if pandas is available)::

    import pandas as pd
    
    df = pd.DataFrame({
        'x': [1, 2, 3, 4],
        'y': [10, 20, 15, 25],
        'category': ['A', 'B', 'A', 'B']
    })

Both work identically with ggoat.

Aesthetic Mappings
------------------

Aesthetics (``aes``) map data to visual properties:

**Position**::

    aes(x='time', y='value')

**Color**::

    aes(x='x', y='y', color='group')

**Size**::

    aes(x='x', y='y', size='importance')

**Multiple Aesthetics**::

    aes(x='gdp', y='life_exp', color='continent', size='population')

**Constant vs Variable Mapping**::

    # Variable mapping (column name)
    aes(color='species')
    
    # Constant value
    .geom_point(color='red', size=3)

Layering Plots
--------------

Combine multiple geometries for rich visualizations::

    (ggplot(data, aes(x='x', y='y'))
     .geom_point(aes(color='group'), size=3)      # Points with color
     .geom_line(color='gray', alpha=0.5)          # Connecting line
     .geom_smooth(method='lm', se=True)           # Trend line
     .labs(title="Multi-layer Plot"))

Customizing Plots
-----------------

**Labels and Titles**::

    .labs(title="My Plot", 
          subtitle="Subtitle here",
          x="X Axis Label", 
          y="Y Axis Label")

**Themes**::

    .theme_minimal()     # Clean minimal theme
    .theme_bw()          # Black and white
    .theme_classic()     # Classic R style

**Scales**::

    .scale_color_manual(['red', 'blue', 'green'])
    .scale_fill_gradient(low='lightblue', high='darkblue')

**Coordinates**::

    .coord_cartesian(xlim=(0, 10), ylim=(0, 100))
    .coord_flip()        # Flip x and y axes

Common Patterns
---------------

**Time Series**::

    time_data = {
        'date': ['2024-01', '2024-02', '2024-03'],
        'value': [100, 120, 110],
        'series': ['A', 'A', 'A']
    }
    
    (ggplot(time_data, aes(x='date', y='value'))
     .geom_line(aes(color='series'), size=2)
     .geom_point(size=3))

**Grouped Bar Chart**::

    (ggplot(data, aes(x='category', y='value', fill='group'))
     .geom_bar(stat='identity', position='dodge')
     .theme_minimal())

**Faceted Plot**::

    (ggplot(data, aes(x='x', y='y'))
     .geom_point()
     .facet_wrap('category')
     .theme_bw())

Saving Plots
------------

Export your plots for sharing::

    # Save as HTML (interactive)
    plot.save('my_plot.html', width=800, height=600)
    
    # Save as JSON (plot specification)
    plot.save('my_plot.json', format='json')

Environment Integration
----------------------

**Jupyter Notebooks**::

    # Plot displays automatically
    plot  # or plot.show()

**Web Applications**::

    # Get HTML for embedding
    html_output = plot.show()

**Pyodide/Browser**::

    # Works seamlessly in browser environments
    plot.show()

Next Steps
----------

Now that you know the basics:

1. **Explore Examples**: :doc:`examples/basic_plots` for copy-paste code
2. **Learn More**: :doc:`tutorials/index` for detailed tutorials  
3. **API Reference**: :doc:`api/index` for complete documentation
4. **Advanced Features**: :doc:`examples/advanced_plots` for complex plots

Tips for Success
----------------

* **Start Simple**: Begin with basic plots and add complexity
* **Use Method Chaining**: It makes code more readable
* **Explore Aesthetics**: Try mapping different variables to color, size, etc.
* **Layer Thoughtfully**: Add layers that enhance understanding
* **Choose Good Themes**: Themes dramatically improve plot appearance

Happy plotting with ggoat! 🐐📊