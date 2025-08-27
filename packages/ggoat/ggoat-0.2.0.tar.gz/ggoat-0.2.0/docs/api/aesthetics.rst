Aesthetics
==========

Aesthetic mappings define how data variables are mapped to visual properties.

.. automodule:: ggoat.aes
   :members:
   :undoc-members:
   :show-inheritance:

aes Class
---------

.. autoclass:: ggoat.aes.aes
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __repr__, __add__

Methods
~~~~~~~

.. automethod:: ggoat.aes.aes.__init__
.. automethod:: ggoat.aes.aes.update
.. automethod:: ggoat.aes.aes.__add__

Supported Aesthetics
--------------------

Position Aesthetics
~~~~~~~~~~~~~~~~~~~

* **x**: Maps to x-axis position
* **y**: Maps to y-axis position

Color Aesthetics  
~~~~~~~~~~~~~~~~

* **color/colour**: Maps to point, line, and text color
* **fill**: Maps to polygon and bar fill color

Size and Shape
~~~~~~~~~~~~~~

* **size**: Maps to point size, line width, text size  
* **shape**: Maps to point shape

Style Aesthetics
~~~~~~~~~~~~~~~~

* **alpha**: Maps to transparency level (0-1)
* **linetype**: Maps to line style (solid, dashed, etc.)

Grouping and Statistics
~~~~~~~~~~~~~~~~~~~~~~

* **group**: Groups observations for geoms like lines
* **weight**: Weights for statistical transformations

Examples
--------

Basic Position Mapping
~~~~~~~~~~~~~~~~~~~~~~

::

    from ggoat import aes
    
    # Map columns to x and y axes
    mapping = aes(x='height', y='weight')

Multiple Aesthetics
~~~~~~~~~~~~~~~~~~~

::

    # Map multiple variables to different aesthetics
    mapping = aes(x='date', y='price', 
                  color='company', size='volume')

Constant vs Variable Mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Variable mapping (uses column name)
    aes(color='species')
    
    # Constant mapping (uses fixed value)  
    aes(color='red')  # Note: use in geom, not aes
    
    # Correct way for constants:
    ggplot(data, aes(x='x', y='y')).geom_point(color='red')

R-Style Compatibility
~~~~~~~~~~~~~~~~~~~~~

::

    # Both spellings work (R compatibility)
    aes(color='group')   # American spelling
    aes(colour='group')  # British spelling

Complex Mappings
~~~~~~~~~~~~~~~~

::

    # Multi-dimensional aesthetic mapping
    complex_aes = aes(
        x='gdp_per_capita',
        y='life_expectancy', 
        color='continent',
        size='population',
        shape='income_level',
        alpha='data_quality'
    )

Combining Aesthetics
~~~~~~~~~~~~~~~~~~~

::

    # Base aesthetics
    base_aes = aes(x='time', y='value')
    
    # Add color mapping
    colored_aes = base_aes + aes(color='group')
    
    # Update with new mapping
    updated_aes = base_aes.update(color='category', size='importance')

Layer-Specific Aesthetics
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Global aesthetics in ggplot()
    plot = ggplot(data, aes(x='x', y='y'))
    
    # Layer-specific aesthetics override global
    plot = (plot
            .geom_point(aes(color='group1'))    # Points colored by group1
            .geom_line(aes(color='group2')))    # Lines colored by group2

Aesthetic Inheritance
~~~~~~~~~~~~~~~~~~~~

::

    # Global aesthetics are inherited by all layers
    plot = ggplot(data, aes(x='time', y='value', color='treatment'))
    
    # Both geoms inherit the color mapping
    plot = plot.geom_point().geom_line()
    
    # Override in specific layer
    plot = plot.geom_smooth(color='red')  # Constant color, ignores global

Common Patterns
---------------

Time Series with Groups
~~~~~~~~~~~~~~~~~~~~~~~

::

    aes(x='date', y='value', color='series', linetype='type')

Scatter Plot with Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    aes(x='x', y='y', color='category', size='magnitude', alpha='confidence')

Bubble Chart
~~~~~~~~~~~~

::

    aes(x='gdp', y='life_exp', size='population', color='continent')

Heatmap
~~~~~~~

::

    aes(x='variable1', y='variable2', fill='correlation')

Bar Chart with Grouping
~~~~~~~~~~~~~~~~~~~~~~~

::

    aes(x='category', y='value', fill='subcategory')

Statistical Plot
~~~~~~~~~~~~~~~~

::

    aes(x='group', y='outcome', color='treatment', weight='sample_size')

Tips
----

1. **Use descriptive names**: Column names should be clear and meaningful
2. **Consider data types**: Continuous vs categorical variables map differently
3. **Layer inheritance**: Global aesthetics apply to all layers unless overridden
4. **Color vs Fill**: Use 'color' for points/lines, 'fill' for bars/areas
5. **Grouping**: Use 'group' aesthetic when you need to group data but don't want visual distinction

See Also
--------

* :doc:`core` - Main ggplot class
* :doc:`geoms` - Geometric objects that use aesthetics
* :doc:`scales` - How aesthetics are displayed