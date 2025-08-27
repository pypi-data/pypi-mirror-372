Core Module
===========

The core module contains the main ggplot class and essential functionality.

.. automodule:: ggoat.core
   :members:
   :undoc-members:
   :show-inheritance:

ggplot Class
------------

.. autoclass:: ggoat.core.ggplot
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Main Methods
~~~~~~~~~~~~

Initialization
^^^^^^^^^^^^^^

.. automethod:: ggoat.core.ggplot.__init__

Geometric Objects
^^^^^^^^^^^^^^^^^

.. automethod:: ggoat.core.ggplot.geom_point
.. automethod:: ggoat.core.ggplot.geom_line  
.. automethod:: ggoat.core.ggplot.geom_bar
.. automethod:: ggoat.core.ggplot.geom_histogram
.. automethod:: ggoat.core.ggplot.geom_smooth
.. automethod:: ggoat.core.ggplot.geom_boxplot
.. automethod:: ggoat.core.ggplot.geom_violin
.. automethod:: ggoat.core.ggplot.geom_density
.. automethod:: ggoat.core.ggplot.geom_area
.. automethod:: ggoat.core.ggplot.geom_text

Labels and Annotations
^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ggoat.core.ggplot.labs
.. automethod:: ggoat.core.ggplot.xlab
.. automethod:: ggoat.core.ggplot.ylab
.. automethod:: ggoat.core.ggplot.ggtitle

Themes
^^^^^^

.. automethod:: ggoat.core.ggplot.theme_minimal
.. automethod:: ggoat.core.ggplot.theme_bw
.. automethod:: ggoat.core.ggplot.theme_classic
.. automethod:: ggoat.core.ggplot.theme_grey
.. automethod:: ggoat.core.ggplot.theme_light
.. automethod:: ggoat.core.ggplot.theme_void
.. automethod:: ggoat.core.ggplot.theme

Scales
^^^^^^

.. automethod:: ggoat.core.ggplot.scale_color_manual
.. automethod:: ggoat.core.ggplot.scale_fill_manual
.. automethod:: ggoat.core.ggplot.scale_color_gradient
.. automethod:: ggoat.core.ggplot.scale_fill_gradient

Coordinates
^^^^^^^^^^^

.. automethod:: ggoat.core.ggplot.coord_cartesian
.. automethod:: ggoat.core.ggplot.coord_flip
.. automethod:: ggoat.core.ggplot.coord_fixed
.. automethod:: ggoat.core.ggplot.coord_polar

Facets
^^^^^^

.. automethod:: ggoat.core.ggplot.facet_wrap
.. automethod:: ggoat.core.ggplot.facet_grid

Plot Building
^^^^^^^^^^^^^

.. automethod:: ggoat.core.ggplot.build
.. automethod:: ggoat.core.ggplot.show
.. automethod:: ggoat.core.ggplot.save

Examples
--------

Basic Usage
~~~~~~~~~~~

Create a simple scatter plot::

    from ggoat import ggplot, aes
    
    data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
    plot = ggplot(data, aes(x='x', y='y')).geom_point()
    plot.show()

Method Chaining
~~~~~~~~~~~~~~~

Build complex plots with method chaining::

    plot = (ggplot(data, aes(x='time', y='value'))
            .geom_point(aes(color='group'), size=3)
            .geom_line(aes(color='group'))
            .theme_minimal()
            .labs(title="Time Series Plot",
                  x="Time", y="Value"))

Multi-layer Plots
~~~~~~~~~~~~~~~~~

Combine multiple geometries::

    plot = (ggplot(data, aes(x='x', y='y'))
            .geom_point(size=3, alpha=0.7)
            .geom_smooth(method='lm', se=True)
            .geom_line(color='gray', alpha=0.5)
            .theme_classic())

Customization
~~~~~~~~~~~~~

Apply custom styling::

    plot = (ggplot(data, aes(x='category', y='value', fill='type'))
            .geom_bar(stat='identity', alpha=0.8)
            .scale_fill_manual(['lightblue', 'lightgreen', 'lightcoral'])
            .coord_flip()
            .theme_minimal()
            .labs(title="Horizontal Bar Chart"))

See Also
--------

* :doc:`aesthetics` - Aesthetic mappings
* :doc:`geoms` - Geometric objects  
* :doc:`themes` - Plot themes
* :doc:`scales` - Scale specifications