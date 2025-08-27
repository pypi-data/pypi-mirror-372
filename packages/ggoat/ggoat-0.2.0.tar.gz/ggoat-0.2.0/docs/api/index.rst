API Reference
=============

Complete reference for all ggoat functions and classes.

Core Components
---------------

.. toctree::
   :maxdepth: 2
   
   core
   aesthetics

Plot Elements
-------------

.. toctree::
   :maxdepth: 2
   
   geoms
   stats
   scales
   coordinates
   facets

Styling
-------

.. toctree::
   :maxdepth: 2
   
   themes
   labels

Integration
-----------

.. toctree::
   :maxdepth: 2
   
   bridge
   utils

Quick Reference
---------------

**Core Classes**:

* :class:`ggoat.ggplot` - Main plotting class
* :class:`ggoat.aes` - Aesthetic mappings

**Essential Methods**:

* :meth:`ggoat.ggplot.geom_point` - Scatter plots
* :meth:`ggoat.ggplot.geom_line` - Line plots
* :meth:`ggoat.ggplot.geom_bar` - Bar charts
* :meth:`ggoat.ggplot.labs` - Labels and titles
* :meth:`ggoat.ggplot.theme_minimal` - Clean theme

**Common Patterns**::

    from ggoat import ggplot, aes
    
    # Basic plot
    ggplot(data, aes(x='x', y='y')).geom_point()
    
    # With styling
    (ggplot(data, aes(x='x', y='y', color='group'))
     .geom_point(size=3)
     .theme_minimal()
     .labs(title="My Plot"))

Function Index
--------------

**Geometries**:
    :func:`geom_point`, :func:`geom_line`, :func:`geom_bar`, :func:`geom_histogram`,
    :func:`geom_boxplot`, :func:`geom_violin`, :func:`geom_density`, :func:`geom_smooth`,
    :func:`geom_area`, :func:`geom_text`, :func:`geom_tile`, :func:`geom_errorbar`

**Statistics**:
    :func:`stat_smooth`, :func:`stat_summary`, :func:`stat_density`, :func:`stat_count`,
    :func:`stat_bin`, :func:`stat_identity`

**Scales**:
    :func:`scale_color_manual`, :func:`scale_fill_manual`, :func:`scale_color_gradient`,
    :func:`scale_fill_gradient`, :func:`scale_x_continuous`, :func:`scale_y_continuous`

**Themes**:
    :func:`theme_minimal`, :func:`theme_bw`, :func:`theme_classic`, :func:`theme_grey`,
    :func:`theme_light`, :func:`theme_void`, :func:`theme`

**Coordinates**:
    :func:`coord_cartesian`, :func:`coord_flip`, :func:`coord_polar`, :func:`coord_fixed`

**Facets**:
    :func:`facet_wrap`, :func:`facet_grid`

**Labels**:
    :func:`labs`, :func:`xlab`, :func:`ylab`, :func:`ggtitle`