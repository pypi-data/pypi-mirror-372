Geometric Objects
=================

Geometric objects (geoms) are the visual elements used to represent data.

Overview
--------

Geoms are the fundamental building blocks of plots in ggoat. They determine how your data is visually represented:

* **Points**: Individual data points (scatter plots)
* **Lines**: Connected data points (line plots, time series)
* **Bars**: Rectangular bars (bar charts, histograms)
* **Areas**: Filled regions (area plots)
* **Text**: Labels and annotations
* **Statistical**: Box plots, violin plots, density plots

All geoms support:
    * Layer-specific aesthetic mappings
    * Statistical transformations
    * Position adjustments
    * Custom styling parameters

Point Geoms
-----------

geom_point()
~~~~~~~~~~~~

Create scatter plots with individual points.

.. code-block:: python

    ggplot(data, aes(x='x', y='y')).geom_point()
    
    # With aesthetics
    ggplot(data, aes(x='x', y='y')).geom_point(
        aes(color='group', size='value'),
        alpha=0.7
    )

**Parameters:**
    * **mapping**: Aesthetic mappings for this layer
    * **data**: Layer-specific data override
    * **alpha**: Transparency (0-1)
    * **color/colour**: Point color
    * **fill**: Point fill color
    * **shape**: Point shape
    * **size**: Point size
    * **stroke**: Outline width

geom_jitter()
~~~~~~~~~~~~~

Jittered points to reduce overplotting.

.. code-block:: python

    ggplot(data, aes(x='category', y='value')).geom_jitter(
        width=0.2, height=0.1, alpha=0.6
    )

Line Geoms
----------

geom_line()
~~~~~~~~~~~

Connect points with lines, ordered by x-axis.

.. code-block:: python

    ggplot(data, aes(x='time', y='value')).geom_line()
    
    # Multiple lines by group
    ggplot(data, aes(x='time', y='value', color='series')).geom_line()

**Parameters:**
    * **alpha**: Line transparency
    * **color/colour**: Line color
    * **linetype**: Line style ('solid', 'dashed', 'dotted')
    * **size**: Line width

geom_path()
~~~~~~~~~~~

Connect points in order they appear in data.

.. code-block:: python

    ggplot(data, aes(x='x', y='y')).geom_path()

geom_step()
~~~~~~~~~~~

Step plots with horizontal then vertical segments.

.. code-block:: python

    ggplot(data, aes(x='x', y='y')).geom_step(direction='hv')

Bar Geoms
---------

geom_bar()
~~~~~~~~~~

Bar charts for categorical data.

.. code-block:: python

    # Count data (default)
    ggplot(data, aes(x='category')).geom_bar()
    
    # Identity (use y values directly)
    ggplot(data, aes(x='category', y='value')).geom_bar(stat='identity')
    
    # Grouped bars
    ggplot(data, aes(x='category', y='value', fill='group')).geom_bar(
        stat='identity', position='dodge'
    )

**Parameters:**
    * **stat**: Statistical transformation ('count' or 'identity')
    * **position**: Position adjustment ('stack', 'dodge', 'fill')
    * **width**: Bar width
    * **alpha**: Transparency
    * **color/colour**: Bar outline color
    * **fill**: Bar fill color

geom_histogram()
~~~~~~~~~~~~~~~~

Histograms for continuous data distribution.

.. code-block:: python

    ggplot(data, aes(x='values')).geom_histogram(bins=30)
    
    # Custom binning
    ggplot(data, aes(x='values')).geom_histogram(
        binwidth=0.5, fill='steelblue', alpha=0.7
    )

Statistical Geoms
-----------------

geom_smooth()
~~~~~~~~~~~~~

Add smoothed conditional means with confidence intervals.

.. code-block:: python

    # Linear model
    ggplot(data, aes(x='x', y='y')).geom_smooth(method='lm')
    
    # Loess smoothing
    ggplot(data, aes(x='x', y='y')).geom_smooth(method='loess', se=True)

**Parameters:**
    * **method**: Smoothing method ('lm', 'loess', 'gam')
    * **se**: Show confidence interval
    * **span**: Smoothing parameter for loess
    * **color/colour**: Line color
    * **fill**: Confidence interval fill

geom_boxplot()
~~~~~~~~~~~~~~

Box plots showing distribution summary.

.. code-block:: python

    ggplot(data, aes(x='group', y='value')).geom_boxplot()
    
    # With outlier customization
    ggplot(data, aes(x='group', y='value')).geom_boxplot(
        outlier_color='red', outlier_size=2
    )

geom_violin()
~~~~~~~~~~~~~

Violin plots showing density distributions.

.. code-block:: python

    ggplot(data, aes(x='group', y='value')).geom_violin()

geom_density()
~~~~~~~~~~~~~~

Density plots for continuous distributions.

.. code-block:: python

    ggplot(data, aes(x='values')).geom_density(fill='lightblue', alpha=0.5)

Area Geoms
----------

geom_area()
~~~~~~~~~~~

Area plots with filled regions.

.. code-block:: python

    ggplot(data, aes(x='x', y='y')).geom_area(fill='lightgreen', alpha=0.6)
    
    # Stacked areas
    ggplot(data, aes(x='x', y='y', fill='group')).geom_area()

Text Geoms
----------

geom_text()
~~~~~~~~~~~

Add text labels to plots.

.. code-block:: python

    ggplot(data, aes(x='x', y='y', label='name')).geom_text()
    
    # With positioning
    ggplot(data, aes(x='x', y='y', label='name')).geom_text(
        hjust=0.5, vjust=-0.5, size=12
    )

**Parameters:**
    * **hjust**: Horizontal justification (0-1)
    * **vjust**: Vertical justification (0-1)
    * **angle**: Text rotation angle
    * **size**: Text size
    * **family**: Font family

Specialized Geoms
-----------------

geom_tile()
~~~~~~~~~~~

Rectangular tiles for heatmaps.

.. code-block:: python

    ggplot(data, aes(x='x', y='y', fill='value')).geom_tile()

geom_errorbar()
~~~~~~~~~~~~~~~

Error bars showing uncertainty.

.. code-block:: python

    ggplot(data, aes(x='group', y='mean', ymin='lower', ymax='upper')).geom_errorbar()

geom_count()
~~~~~~~~~~~~

Count overlapping points by sizing.

.. code-block:: python

    ggplot(data, aes(x='x', y='y')).geom_count()

Position Adjustments
--------------------

Control how geoms handle overlapping data:

* **identity**: No adjustment (default for most geoms)
* **stack**: Stack overlapping objects (bars, areas)
* **dodge**: Place side by side (bars)
* **fill**: Stack to 100% (bars, areas)
* **jitter**: Add random noise (points)

.. code-block:: python

    # Dodged bars
    ggplot(data, aes(x='category', y='value', fill='group')).geom_bar(
        stat='identity', position='dodge'
    )
    
    # Jittered points
    ggplot(data, aes(x='group', y='value')).geom_point(position='jitter')

Common Patterns
---------------

Multi-layer Plots
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Points + line + smooth
    (ggplot(data, aes(x='x', y='y'))
     .geom_point(alpha=0.5)
     .geom_line(color='gray')
     .geom_smooth(method='lm', color='red'))

Time Series
~~~~~~~~~~~

.. code-block:: python

    # Multiple series
    (ggplot(data, aes(x='date', y='value', color='series'))
     .geom_line(size=1)
     .geom_point(size=2))

Distribution Comparison
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Overlapping densities
    (ggplot(data, aes(x='value', fill='group'))
     .geom_density(alpha=0.6)
     .geom_histogram(alpha=0.3, position='identity'))

Tips
----

1. **Layer Order Matters**: Later layers appear on top
2. **Use Alpha**: Transparency helps with overplotting
3. **Position Adjustments**: Essential for categorical data
4. **Combine Geoms**: Layer different geoms for rich visualizations
5. **Aesthetic Inheritance**: Global aesthetics apply to all layers

See Also
--------

* :doc:`aesthetics` - How to map data to visual properties
* :doc:`scales` - Control how aesthetics are displayed
* :doc:`core` - Main ggplot class with geom methods