"""
Aesthetic mappings for ggplot visualizations.

This module provides the aesthetic mapping system for ggoat, which defines how
data variables are mapped to visual properties (aesthetics) of geometric objects.
Aesthetic mappings are the bridge between your data and the visual representation.

The aesthetic mapping system supports:
    * Position aesthetics (x, y)
    * Color and fill aesthetics (color/colour, fill)
    * Size and shape aesthetics (size, shape)
    * Transparency and line aesthetics (alpha, linetype)
    * Grouping and weight aesthetics (group, weight)
    * Statistical aesthetics (weight for weighted operations)
    * Custom aesthetics via keyword arguments

Key Concepts:
    * Variable mapping: String column names map data variables to aesthetics
    * Constant values: Non-string values create constant aesthetics
    * R compatibility: Supports both 'color' and 'colour' spellings
    * Inheritance: Default aesthetics can be overridden in layers
    * Composition: Aesthetic mappings can be combined and updated

Example:
    Basic aesthetic mappings::

        from ggoat import aes

        # Position mappings
        mapping = aes(x='time', y='value')

        # With color and size
        mapping = aes(x='x', y='y', color='group', size='magnitude')

        # Mixing variables and constants
        mapping = aes(x='date', y='price', color='red', size=3)

        # Complex mappings
        mapping = aes(x='x', y='y', color='category',
                     size='importance', alpha='confidence',
                     linetype='treatment')

Authors:
    ggoat development team

License:
    MIT License
"""

from typing import Any, Optional, Union


class aes:
    """
    Define aesthetic mappings between data variables and visual properties.

    The aes class creates aesthetic mappings that specify how variables in your
    data are mapped to visual properties of geometric objects. These mappings
    form the foundation of the Grammar of Graphics approach to data visualization.

    Aesthetic mappings can specify:

    Position Aesthetics:
        * x: Maps to x-axis position
        * y: Maps to y-axis position

    Color Aesthetics:
        * color/colour: Maps to point, line, and text color
        * fill: Maps to polygon and bar fill color

    Size and Shape:
        * size: Maps to point size, line width, text size
        * shape: Maps to point shape

    Transparency and Style:
        * alpha: Maps to transparency level (0-1)
        * linetype: Maps to line style (solid, dashed, dotted, etc.)

    Grouping and Statistics:
        * group: Groups observations for geoms like lines
        * weight: Weights for statistical transformations

    The aesthetic mapping system distinguishes between:
        * Variable mappings: String column names (e.g., color='species')
        * Constant values: Fixed values (e.g., color='red', size=3)

    Mappings can be inherited from the base ggplot() call or specified
    locally in individual geom layers, with layer mappings taking precedence.

    Attributes:
        mapping (dict): Dictionary storing the aesthetic mappings

    Examples:
        Basic position mapping::

            aes(x='height', y='weight')

        Multiple aesthetics::

            aes(x='date', y='price', color='company', size='volume')

        Mixing variables and constants::

            aes(x='time', y='value', color='group', alpha=0.7)

        Complex multi-aesthetic mapping::

            aes(x='gdp_per_capita', y='life_expectancy',
                color='continent', size='population',
                shape='income_level', alpha='data_quality')

        R-style color specification::

            aes(x='x', y='y', colour='group')  # British spelling

    Note:
        The aes object is immutable. Operations like update() and __add__()
        return new aes objects rather than modifying the original.
    """

    def __init__(
        self,
        x: Optional[Union[str, Any]] = None,
        y: Optional[Union[str, Any]] = None,
        color: Optional[Union[str, Any]] = None,
        colour: Optional[Union[str, Any]] = None,
        fill: Optional[Union[str, Any]] = None,
        size: Optional[Union[str, Any]] = None,
        shape: Optional[Union[str, Any]] = None,
        alpha: Optional[Union[str, Any]] = None,
        linetype: Optional[Union[str, Any]] = None,
        weight: Optional[Union[str, Any]] = None,
        group: Optional[Union[str, Any]] = None,
        **kwargs,
    ):
        """
        Create aesthetic mappings.

        Args:
            x: Variable mapped to x-axis
            y: Variable mapped to y-axis
            color/colour: Variable mapped to color aesthetic
            fill: Variable mapped to fill aesthetic
            size: Variable mapped to size aesthetic
            shape: Variable mapped to shape aesthetic
            alpha: Variable mapped to alpha (transparency) aesthetic
            linetype: Variable mapped to linetype aesthetic
            weight: Variable mapped to weight aesthetic
            group: Variable mapped to grouping aesthetic
            **kwargs: Additional aesthetic mappings
        """
        self.mapping = {}

        # Standard aesthetics
        if x is not None:
            self.mapping["x"] = self._process_aesthetic(x)
        if y is not None:
            self.mapping["y"] = self._process_aesthetic(y)

        # Color can be specified as 'color' or 'colour' (R compatibility)
        color_val = color if color is not None else colour
        if color_val is not None:
            self.mapping["color"] = self._process_aesthetic(color_val)

        if fill is not None:
            self.mapping["fill"] = self._process_aesthetic(fill)
        if size is not None:
            self.mapping["size"] = self._process_aesthetic(size)
        if shape is not None:
            self.mapping["shape"] = self._process_aesthetic(shape)
        if alpha is not None:
            self.mapping["alpha"] = self._process_aesthetic(alpha)
        if linetype is not None:
            self.mapping["linetype"] = self._process_aesthetic(linetype)
        if weight is not None:
            self.mapping["weight"] = self._process_aesthetic(weight)
        if group is not None:
            self.mapping["group"] = self._process_aesthetic(group)

        # Additional aesthetics from kwargs
        for key, value in kwargs.items():
            if value is not None:
                self.mapping[key] = self._process_aesthetic(value)

    def _process_aesthetic(self, value: Union[str, Any]) -> Union[str, Any]:
        """
        Process an aesthetic value.

        If the value is a string, it's treated as a column name.
        Otherwise, it's treated as a constant value.

        Args:
            value: The aesthetic value

        Returns:
            Processed aesthetic value
        """
        if isinstance(value, str):
            # Column reference
            return value
        else:
            # Constant value - will need special handling in lets-plot
            return value

    def __repr__(self) -> str:
        """String representation of aesthetic mappings."""
        mappings = [
            f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}"
            for k, v in self.mapping.items()
        ]
        return f"aes({', '.join(mappings)})"

    def __add__(self, other: "aes") -> "aes":
        """
        Combine aesthetic mappings.

        Args:
            other: Another aes object

        Returns:
            New aes object with combined mappings
        """
        new_aes = aes()
        new_aes.mapping = {**self.mapping, **other.mapping}
        return new_aes

    def update(self, **kwargs) -> "aes":
        """
        Update aesthetic mappings.

        Args:
            **kwargs: New aesthetic mappings to add/update

        Returns:
            New aes object with updated mappings
        """
        new_mappings = {}
        for key, value in kwargs.items():
            if value is not None:
                new_mappings[key] = self._process_aesthetic(value)

        new_aes = aes()
        new_aes.mapping = {**self.mapping, **new_mappings}
        return new_aes
