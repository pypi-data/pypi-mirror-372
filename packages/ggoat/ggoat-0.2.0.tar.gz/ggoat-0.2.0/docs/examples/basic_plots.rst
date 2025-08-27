Basic Plot Examples
===================

Ready-to-use examples for common plot types with ggoat.

Scatter Plots
-------------

Basic Scatter Plot
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ggoat import ggplot, aes
    
    data = {
        'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'y': [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        'group': ['A', 'A', 'B', 'B', 'C', 'C', 'A', 'A', 'B', 'B']
    }
    
    plot = (ggplot(data, aes(x='x', y='y'))
            .geom_point(size=3, color='steelblue')
            .labs(title="Basic Scatter Plot", x="X Values", y="Y Values")
            .theme_minimal())
    
    plot.show()

Colored by Group
~~~~~~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(data, aes(x='x', y='y', color='group'))
            .geom_point(size=4, alpha=0.7)
            .labs(title="Scatter Plot by Group")
            .theme_minimal())

Bubble Chart
~~~~~~~~~~~~

.. code-block:: python

    bubble_data = {
        'x': [1, 2, 3, 4, 5],
        'y': [10, 20, 15, 25, 30],
        'size': [5, 10, 15, 8, 12],
        'category': ['A', 'B', 'A', 'C', 'B']
    }
    
    plot = (ggplot(bubble_data, aes(x='x', y='y', size='size', color='category'))
            .geom_point(alpha=0.6)
            .labs(title="Bubble Chart")
            .theme_classic())

Line Plots
----------

Simple Line Plot
~~~~~~~~~~~~~~~~

.. code-block:: python

    time_data = {
        'day': [1, 2, 3, 4, 5, 6, 7],
        'temperature': [20, 22, 25, 23, 27, 29, 26]
    }
    
    plot = (ggplot(time_data, aes(x='day', y='temperature'))
            .geom_line(size=2, color='orange')
            .geom_point(size=3, color='red')
            .labs(title="Daily Temperature", x="Day", y="Temperature (°C)")
            .theme_bw())

Multiple Lines
~~~~~~~~~~~~~~

.. code-block:: python

    multi_series = {
        'time': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        'value': [10, 15, 12, 18, 20, 8, 12, 14, 16, 22],
        'series': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B']
    }
    
    plot = (ggplot(multi_series, aes(x='time', y='value', color='series'))
            .geom_line(size=2)
            .geom_point(size=3)
            .labs(title="Multiple Time Series")
            .theme_minimal())

Line with Confidence Band
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(data, aes(x='x', y='y'))
            .geom_point(alpha=0.5)
            .geom_smooth(method='lm', se=True, color='red')
            .labs(title="Line with Confidence Interval")
            .theme_classic())

Bar Charts
----------

Simple Bar Chart
~~~~~~~~~~~~~~~~

.. code-block:: python

    category_data = {
        'category': ['A', 'B', 'C', 'D', 'E'],
        'value': [23, 45, 56, 78, 32]
    }
    
    plot = (ggplot(category_data, aes(x='category', y='value'))
            .geom_bar(stat='identity', fill='steelblue', alpha=0.8)
            .labs(title="Bar Chart", x="Categories", y="Values")
            .theme_minimal())

Grouped Bar Chart
~~~~~~~~~~~~~~~~~

.. code-block:: python

    grouped_data = {
        'category': ['A', 'A', 'B', 'B', 'C', 'C'],
        'value': [10, 15, 20, 25, 30, 35],
        'group': ['X', 'Y', 'X', 'Y', 'X', 'Y']
    }
    
    plot = (ggplot(grouped_data, aes(x='category', y='value', fill='group'))
            .geom_bar(stat='identity', position='dodge', alpha=0.8)
            .labs(title="Grouped Bar Chart")
            .theme_bw())

Horizontal Bar Chart
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(category_data, aes(x='category', y='value'))
            .geom_bar(stat='identity', fill='darkgreen', alpha=0.7)
            .coord_flip()
            .labs(title="Horizontal Bar Chart")
            .theme_minimal())

Histograms
----------

Basic Histogram
~~~~~~~~~~~~~~~

.. code-block:: python

    import random
    
    # Generate sample data
    hist_data = {
        'values': [random.gauss(50, 15) for _ in range(1000)]
    }
    
    plot = (ggplot(hist_data, aes(x='values'))
            .geom_histogram(bins=30, fill='lightblue', color='navy', alpha=0.7)
            .labs(title="Distribution of Values", x="Values", y="Frequency")
            .theme_classic())

Overlapping Histograms
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Two groups
    overlap_data = {
        'values': ([random.gauss(45, 10) for _ in range(500)] + 
                  [random.gauss(55, 12) for _ in range(500)]),
        'group': (['A'] * 500 + ['B'] * 500)
    }
    
    plot = (ggplot(overlap_data, aes(x='values', fill='group'))
            .geom_histogram(bins=25, alpha=0.6, position='identity')
            .labs(title="Overlapping Distributions")
            .theme_minimal())

Box Plots
---------

Basic Box Plot
~~~~~~~~~~~~~~

.. code-block:: python

    box_data = {
        'group': (['A'] * 50 + ['B'] * 50 + ['C'] * 50),
        'value': ([random.gauss(20, 5) for _ in range(50)] +
                 [random.gauss(25, 7) for _ in range(50)] +
                 [random.gauss(30, 6) for _ in range(50)])
    }
    
    plot = (ggplot(box_data, aes(x='group', y='value'))
            .geom_boxplot(fill='lightgreen', alpha=0.7)
            .labs(title="Box Plot by Group")
            .theme_bw())

Box Plot with Points
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(box_data, aes(x='group', y='value'))
            .geom_boxplot(alpha=0.7)
            .geom_jitter(width=0.2, alpha=0.5, color='red')
            .labs(title="Box Plot with Data Points")
            .theme_minimal())

Density Plots
-------------

Basic Density Plot
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(hist_data, aes(x='values'))
            .geom_density(fill='orange', alpha=0.6)
            .labs(title="Density Plot")
            .theme_classic())

Multiple Densities
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(overlap_data, aes(x='values', fill='group'))
            .geom_density(alpha=0.5)
            .labs(title="Density Plot by Group")
            .theme_minimal())

Statistical Plots
-----------------

Correlation Plot
~~~~~~~~~~~~~~~~

.. code-block:: python

    corr_data = {
        'x': [i + random.gauss(0, 2) for i in range(1, 21)],
        'y': [2*i + random.gauss(0, 3) for i in range(1, 21)]
    }
    
    plot = (ggplot(corr_data, aes(x='x', y='y'))
            .geom_point(size=3, alpha=0.7)
            .geom_smooth(method='lm', se=True)
            .labs(title="Correlation Analysis", 
                  subtitle="Points with linear trend")
            .theme_minimal())

Violin Plot
~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(box_data, aes(x='group', y='value'))
            .geom_violin(fill='purple', alpha=0.6)
            .geom_boxplot(width=0.1, fill='white', alpha=0.8)
            .labs(title="Violin Plot with Box Plot")
            .theme_bw())

Multi-layer Plots
-----------------

Points + Lines + Smooth
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    complex_data = {
        'x': [i for i in range(1, 21)],
        'y': [i*2 + random.gauss(0, 5) for i in range(1, 21)],
        'group': ['A']*10 + ['B']*10
    }
    
    plot = (ggplot(complex_data, aes(x='x', y='y', color='group'))
            .geom_point(size=3, alpha=0.7)
            .geom_line(alpha=0.5)
            .geom_smooth(method='lm', se=False, size=2)
            .labs(title="Multi-layer Visualization")
            .theme_classic())

Mixed Geoms
~~~~~~~~~~~

.. code-block:: python

    mixed_data = {
        'category': ['A', 'B', 'C', 'D'],
        'value': [25, 45, 35, 55],
        'error': [3, 5, 4, 6]
    }
    
    plot = (ggplot(mixed_data, aes(x='category', y='value'))
            .geom_bar(stat='identity', fill='lightblue', alpha=0.7)
            .geom_errorbar(aes(ymin='value', ymax='value'), width=0.2)
            .geom_text(aes(label='value'), vjust=-0.5)
            .labs(title="Bar Chart with Error Bars and Labels")
            .theme_minimal())

Customization Examples
---------------------

Custom Colors
~~~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(grouped_data, aes(x='category', y='value', fill='group'))
            .geom_bar(stat='identity', position='dodge')
            .scale_fill_manual(['#FF6B6B', '#4ECDC4'])
            .labs(title="Custom Color Palette")
            .theme_minimal())

Custom Theme
~~~~~~~~~~~~

.. code-block:: python

    plot = (ggplot(data, aes(x='x', y='y', color='group'))
            .geom_point(size=4)
            .theme_void()
            .labs(title="Minimal Theme")
            .theme(legend_position='bottom'))

Faceted Plot
~~~~~~~~~~~~

.. code-block:: python

    facet_data = {
        'x': [i for i in range(1, 21)] * 3,
        'y': [random.gauss(i, 2) for i in range(1, 21)] * 3,
        'category': ['Type A']*20 + ['Type B']*20 + ['Type C']*20
    }
    
    plot = (ggplot(facet_data, aes(x='x', y='y'))
            .geom_point(color='steelblue', size=2)
            .geom_smooth(method='lm', se=False, color='red')
            .facet_wrap('category')
            .labs(title="Faceted Plot")
            .theme_bw())

Tips for Better Plots
---------------------

1. **Choose appropriate geoms** for your data type
2. **Use transparency (alpha)** to handle overplotting
3. **Apply consistent themes** for professional appearance
4. **Add meaningful labels** and titles
5. **Consider color accessibility** in your palette choices
6. **Layer thoughtfully** - order matters for visibility

Next Steps
----------

* :doc:`advanced_plots` - Complex visualizations
* :doc:`../api/index` - Complete API reference
* :doc:`../tutorials/index` - Step-by-step tutorials