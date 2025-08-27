"""
Core ggplot class implementing the Grammar of Graphics API with method chaining.

This module provides the main ggplot class that implements a Grammar of Graphics
interface optimized for Pyodide and browser environments. The API uses method
chaining instead of the traditional "+" operator for fluent, readable syntax.

Key Features:
    * Method chaining for readable plot construction
    * Support for all major geom types (point, line, bar, histogram, etc.)
    * Comprehensive aesthetic mappings (color, size, shape, alpha)
    * Built-in themes and color schemes
    * Faceting and coordinate systems
    * Statistical transformations and position adjustments
    * Export capabilities (HTML, JSON)
    * Integration with lets-plot rendering engine
    * Optimized for minimal dependencies

Example:
    Basic scatter plot with method chaining::

        from ggoat import ggplot, aes

        data = {'x': [1, 2, 3], 'y': [4, 5, 6], 'group': ['A', 'B', 'A']}

        plot = (ggplot(data, aes(x='x', y='y', color='group'))
                .geom_point(size=3, alpha=0.7)
                .labs(title="My Plot", x="X Values", y="Y Values")
                .theme_minimal())

        plot.show()

Authors:
    ggoat development team

License:
    MIT License
"""

from typing import Any, Dict, List, Optional, Union

try:
    import numpy as np
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    pd = None
    np = None
    HAS_PANDAS = False

from .aes import aes
from .bridge import LetsPlotBridge


class ggplot:
    """
    Main ggplot class implementing Grammar of Graphics with method chaining.

    The ggplot class is the core of the ggoat package, providing a Grammar of Graphics
    interface that uses method chaining for plot construction. Each method returns a new
    ggplot object, allowing for fluent and readable plot building.

    The Grammar of Graphics separates plot construction into distinct components:
    - Data: The dataset being visualized
    - Aesthetics: How data variables map to visual properties
    - Geometries: The geometric objects that represent data
    - Statistics: Statistical transformations applied to data
    - Scales: How aesthetic mappings are displayed
    - Coordinates: The coordinate system
    - Facets: Small multiples based on subsets
    - Themes: Overall visual styling

    This implementation is optimized for Pyodide and browser environments with:
    - Minimal dependencies (works with just Python stdlib)
    - Method chaining instead of "+" operator
    - Support for both dict and pandas DataFrame data
    - Integration with lets-plot JavaScript rendering
    - Export capabilities for web deployment

    Attributes:
        data: The dataset for the plot (dict or DataFrame)
        mapping: Default aesthetic mappings (aes object)
        layers: List of plot layers (geoms, stats, etc.)
        scales: Dictionary of scale specifications
        labels: Plot and axis labels
        theme: Theme settings
        coords: Coordinate system settings
        facets: Faceting configuration
        bridge: Rendering bridge to lets-plot

    Examples:
        Basic scatter plot::

            data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
            plot = ggplot(data, aes(x='x', y='y')).geom_point()

        Complex multi-layer plot::

            plot = (ggplot(data, aes(x='time', y='value'))
                    .geom_point(aes(color='group'), size=3)
                    .geom_line(aes(color='group'))
                    .geom_smooth(method='lm', se=True)
                    .facet_wrap('category')
                    .labs(title="Time Series Analysis")
                    .theme_minimal())

        With custom styling::

            plot = (ggplot(data, aes(x='x', y='y'))
                    .geom_point(color='steelblue', size=4, alpha=0.7)
                    .scale_color_manual(['red', 'blue', 'green'])
                    .coord_cartesian(xlim=(0, 10), ylim=(0, 100))
                    .theme(legend_position='bottom'))
    """

    # ========================================================================
    # COORDINATE SYSTEMS
    # ========================================================================
    def coord_fixed(self, ratio=1, xlim=None, ylim=None, expand=True, **kwargs):
        """
        Fixed scale coordinate system (forces aspect ratio).
        """
        new_plot = self._copy()
        coord = {
            "type": "fixed",
            "ratio": ratio,
            "xlim": xlim,
            "ylim": ylim,
            "expand": expand,
        }
        coord.update(kwargs)
        new_plot.coords = coord
        return new_plot

    def coord_polar(self, theta="x", start=0, direction=1, **kwargs):
        """
        Polar coordinate system.
        """
        new_plot = self._copy()
        coord = {
            "type": "polar",
            "theta": theta,
            "start": start,
            "direction": direction,
        }
        coord.update(kwargs)
        new_plot.coords = coord
        return new_plot

    def coord_map(
        self,
        projection="mercator",
        xlim=None,
        ylim=None,
        expand=True,
        **kwargs,
    ):
        """
        Map projection coordinate system.
        """
        new_plot = self._copy()
        coord = {
            "type": "map",
            "projection": projection,
            "xlim": xlim,
            "ylim": ylim,
            "expand": expand,
        }
        coord.update(kwargs)
        new_plot.coords = coord
        return new_plot

    # ========================================================================
    # FLAVORS (COLOR SCHEMES)
    # ========================================================================
    def flavor_darcula(self):
        """Apply Darcula color scheme."""
        new_plot = self._copy()
        new_plot.theme = {"flavor": "darcula"}
        return new_plot

    def flavor_high_contrast_dark(self):
        """Apply high contrast dark color scheme."""
        new_plot = self._copy()
        new_plot.theme = {"flavor": "high_contrast_dark"}
        return new_plot

    def flavor_high_contrast_light(self):
        """Apply high contrast light color scheme."""
        new_plot = self._copy()
        new_plot.theme = {"flavor": "high_contrast_light"}
        return new_plot

    def flavor_solarized_dark(self):
        """Apply solarized dark color scheme."""
        new_plot = self._copy()
        new_plot.theme = {"flavor": "solarized_dark"}
        return new_plot

    def flavor_solarized_light(self):
        """Apply solarized light color scheme."""
        new_plot = self._copy()
        new_plot.theme = {"flavor": "solarized_light"}
        return new_plot

    # ========================================================================
    # TOOLTIP LAYERS
    # ========================================================================
    def layer_tooltips(self, **kwargs):
        """
        Configure tooltips for the plot.
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "tooltips"):
            new_plot.tooltips = {}
        new_plot.tooltips.update(kwargs)
        return new_plot

    # ========================================================================
    # FONT FEATURES
    # ========================================================================
    def font_metrics_adjustment(self, **kwargs):
        """
        Adjust estimated width of text labels on plot.
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "font_metrics"):
            new_plot.font_metrics = {}
        new_plot.font_metrics.update(kwargs)
        return new_plot

    def font_family_info(self, **kwargs):
        """
        Specify properties of a particular font-family.
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "font_family_info"):
            new_plot.font_family_info = {}
        new_plot.font_family_info.update(kwargs)
        return new_plot

    # ========================================================================
    # SAMPLING METHODS
    # ========================================================================
    def sampling_random(self, n=None, **kwargs):
        """
        Randomly sample n items from the data.
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "sampling"):
            new_plot.sampling = []
        new_plot.sampling.append({"type": "random", "n": n, **kwargs})
        return new_plot

    def sampling_random_stratified(self, strata=None, n=None, **kwargs):
        """
        Randomly sample from each stratum (subgroup).
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "sampling"):
            new_plot.sampling = []
        new_plot.sampling.append(
            {"type": "random_stratified", "strata": strata, "n": n, **kwargs}
        )
        return new_plot

    def sampling_pick(self, n=None, **kwargs):
        """
        Pick sampling (first n items).
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "sampling"):
            new_plot.sampling = []
        new_plot.sampling.append({"type": "pick", "n": n, **kwargs})
        return new_plot

    def sampling_systematic(self, interval=None, **kwargs):
        """
        Systematic sampling (every k-th item).
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "sampling"):
            new_plot.sampling = []
        new_plot.sampling.append({"type": "systematic", "interval": interval, **kwargs})
        return new_plot

    def sampling_group_random(self, n=None, **kwargs):
        """
        Randomly sample n groups.
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "sampling"):
            new_plot.sampling = []
        new_plot.sampling.append({"type": "group_random", "n": n, **kwargs})
        return new_plot

    def sampling_group_systematic(self, interval=None, **kwargs):
        """
        Systematic group sampling (every k-th group).
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "sampling"):
            new_plot.sampling = []
        new_plot.sampling.append(
            {"type": "group_systematic", "interval": interval, **kwargs}
        )
        return new_plot

    def sampling_vertex_vw(self, **kwargs):
        """
        Simplify a polyline using the Visvalingam-Whyatt algorithm.
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "sampling"):
            new_plot.sampling = []
        new_plot.sampling.append({"type": "vertex_vw", **kwargs})
        return new_plot

    def sampling_vertex_dp(self, **kwargs):
        """
        Simplify a polyline using the Douglas-Peucker algorithm.
        """
        new_plot = self._copy()
        if not hasattr(new_plot, "sampling"):
            new_plot.sampling = []
        new_plot.sampling.append({"type": "vertex_dp", **kwargs})
        return new_plot

    """
    Core ggplot class that implements the Grammar of Graphics with method chaining.

    This class builds plots by chaining methods:
    - Data and aesthetic mappings
    - Geometric objects (geoms)
    - Statistical transformations (stats)
    - Scales
    - Coordinate systems
    - Facets
    - Themes
    - Labels

    Usage:
        ggplot(data, aes(x='col1', y='col2')).geom_point().labs(title="My Plot")
    """

    def __init__(self, data: Optional[Any] = None, mapping: Optional["aes"] = None):
        """
        Initialize a ggplot object.

        Creates a new ggplot object with the specified data and aesthetic mappings.
        This is the starting point for all plot construction in ggoat.

        Args:
            data: The dataset to visualize. Can be:
                - dict: Dictionary with column names as keys and lists as values
                - pandas.DataFrame: If pandas is available
                - None: For plots that don't require data (e.g., function plots)
            mapping: Default aesthetic mappings created with aes(). These mappings
                apply to all layers unless overridden. Common aesthetics include:
                - x, y: Position mappings
                - color, colour: Color mappings
                - size: Size mappings
                - shape: Shape mappings
                - alpha: Transparency mappings
                - fill: Fill color mappings

        Returns:
            A new ggplot object ready for method chaining.

        Examples:
            Basic initialization::

                data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
                p = ggplot(data, aes(x='x', y='y'))

            With multiple aesthetics::

                data = {'x': [1, 2, 3], 'y': [4, 5, 6], 'group': ['A', 'B', 'A']}
                p = ggplot(data, aes(x='x', y='y', color='group'))

            No default mapping (set in layers)::

                p = ggplot(data)  # Aesthetics specified in geom layers

        Note:
            The ggplot object is immutable - each method call returns a new object.
            This allows for safe plot composition and reuse of base plots.
        """
        self.data = data
        self.mapping = mapping
        self.layers = []  # type: list[dict[str, Any]]
        self.scales = {}  # type: dict[str, Any]
        self.labels = {}  # type: dict[str, Any]
        self._theme_dict = {}  # type: dict[str, Any]
        self.coords = None
        self.facets = None
        self.bridge = LetsPlotBridge()

    def _copy(self):
        """Create a copy of the current ggplot object for method chaining."""
        new_plot = ggplot(self.data, self.mapping)
        new_plot.layers = self.layers.copy()
        new_plot.scales = self.scales.copy()
        new_plot.labels = self.labels.copy()
        new_plot._theme_dict = (
            self._theme_dict.copy() if hasattr(self._theme_dict, "copy") else self._theme_dict
        )
        new_plot.coords = self.coords
        new_plot.facets = self.facets
        new_plot.bridge = self.bridge
        return new_plot

    # ========================================================================
    # GEOMETRIC OBJECTS (GEOMS)
    # ========================================================================

    def geom_point(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        shape: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        stroke: Optional[float] = None,
        **kwargs,
    ):
        """
        Add scatter plot points.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Point color
            fill: Point fill color
            shape: Point shape
            size: Point size
            stroke: Stroke width for point outline
            **kwargs: Additional parameters

        Returns:
            New ggplot object with point layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "shape": shape,
                "size": size,
                "stroke": stroke,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "point",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_line(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Add line plots.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Line color
            linetype: Line type (solid, dashed, etc.)
            size: Line size/width
            **kwargs: Additional parameters

        Returns:
            New ggplot object with line layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "line",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_bar(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "count",
        position="stack",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        width: Optional[float] = None,
        **kwargs,
    ):
        """
        Add bar charts.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation ("count" or "identity")
            position: Position adjustment ("stack", "dodge", "fill")
            alpha: Transparency (0-1)
            color/colour: Bar outline color
            fill: Bar fill color
            linetype: Outline line type
            size: Outline line size
            width: Bar width
            **kwargs: Additional parameters

        Returns:
            New ggplot object with bar layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "linetype": linetype,
                "size": size,
                "width": width,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "bar",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_histogram(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "bin",
        position: str = "stack",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        bins: Optional[int] = 30,
        binwidth: Optional[float] = None,
        **kwargs,
    ):
        """
        Add histograms.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Bar outline color
            fill: Bar fill color
            linetype: Outline line type
            size: Outline line size
            bins: Number of bins
            binwidth: Width of bins
            **kwargs: Additional parameters

        Returns:
            New ggplot object with histogram layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "linetype": linetype,
                "size": size,
                "bins": bins,
                "binwidth": binwidth,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "histogram",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_smooth(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "smooth",
        position: str = "identity",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        method: str = "loess",
        se: bool = True,
        span: Optional[float] = None,
        **kwargs,
    ):
        """
        Add smoothed conditional means.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Line color
            fill: Confidence interval fill color
            linetype: Line type
            size: Line size
            method: Smoothing method ("loess", "lm", "gam", etc.)
            se: Display confidence interval
            span: Controls the degree of smoothing (for loess)
            **kwargs: Additional parameters

        Returns:
            New ggplot object with smooth layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "linetype": linetype,
                "size": size,
                "method": method,
                "se": se,
                "span": span,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "smooth",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_boxplot(
        self,
        mapping: Optional["aes"] = None,
        data: Optional[Any] = None,
        stat: str = "boxplot",
        position: str = "dodge2",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        width: Optional[float] = None,
        outlier_alpha: Optional[float] = None,
        outlier_color: Optional[str] = None,
        outlier_colour: Optional[str] = None,
        outlier_fill: Optional[str] = None,
        outlier_shape: Optional[Union[int, str]] = None,
        outlier_size: Optional[float] = None,
        outlier_stroke: Optional[float] = None,
        notch: bool = False,
        notchwidth: Optional[float] = 0.5,
        varwidth: bool = False,
        **kwargs,
    ):
        """
        Add a boxplot layer to the plot.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Box outline color
            fill: Box fill color
            linetype: Outline line type
            size: Outline line size
            width: Box width
            outlier_*: Outlier point aesthetics
            notch: Whether to draw notched boxes
            notchwidth: Relative width of notches
            varwidth: Whether to make box widths proportional to sqrt(n)
            **kwargs: Additional parameters

        Returns:
            New ggplot object with boxplot layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour
        if outlier_color is None and outlier_colour is not None:
            outlier_color = outlier_colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "linetype": linetype,
                "size": size,
                "width": width,
                "outlier_alpha": outlier_alpha,
                "outlier_color": outlier_color,
                "outlier_fill": outlier_fill,
                "outlier_shape": outlier_shape,
                "outlier_size": outlier_size,
                "outlier_stroke": outlier_stroke,
                "notch": notch,
                "notchwidth": notchwidth,
                "varwidth": varwidth,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "boxplot",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_violin(
        self,
        mapping: Optional["aes"] = None,
        data: Optional[Any] = None,
        stat: str = "ydensity",
        position: str = "dodge",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        width: Optional[float] = None,
        trim: bool = True,
        scale: str = "area",
        draw_quantiles: Optional[list] = None,
        **kwargs,
    ):
        """
        Add a violin plot layer to the plot.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Violin outline color
            fill: Violin fill color
            linetype: Outline line type
            size: Outline line size
            width: Violin width
            trim: Whether to trim tails to data range
            scale: How to scale violins ("area", "count", "width")
            draw_quantiles: Quantile lines to draw
            **kwargs: Additional parameters

        Returns:
            New ggplot object with violin layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "linetype": linetype,
                "size": size,
                "width": width,
                "trim": trim,
                "scale": scale,
                "draw_quantiles": draw_quantiles,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "violin",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_text(
        self,
        mapping: Optional["aes"] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        alpha: Optional[float] = None,
        angle: Optional[float] = 0,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        family: Optional[str] = None,
        fontface: Optional[Union[str, int]] = None,
        hjust: Optional[Union[float, str]] = None,
        lineheight: Optional[float] = None,
        size: Optional[float] = None,
        vjust: Optional[Union[float, str]] = None,
        check_overlap: bool = False,
        **kwargs,
    ):
        """
        Add text annotations to the plot.

        Args:
            mapping: Aesthetic mappings (must include 'label')
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            angle: Text angle in degrees
            color/colour: Text color
            family: Font family
            fontface: Font face
            hjust: Horizontal justification
            lineheight: Line height multiplier
            size: Text size
            vjust: Vertical justification
            check_overlap: Whether to check for overlapping text
            **kwargs: Additional parameters

        Returns:
            New ggplot object with text layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "angle": angle,
                "color": color,
                "family": family,
                "fontface": fontface,
                "hjust": hjust,
                "lineheight": lineheight,
                "size": size,
                "vjust": vjust,
                "check_overlap": check_overlap,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "text",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_jitter(
        self,
        mapping: Optional["aes"] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "jitter",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        shape: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        stroke: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        **kwargs,
    ):
        """
        Add jittered points to the plot.

        Args:
            mapping: Aesthetic mappings
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment (default: "jitter")
            alpha: Transparency (0-1)
            color/colour: Point color
            fill: Point fill color
            shape: Point shape
            size: Point size
            stroke: Stroke width for point outline
            width: Jitter width
            height: Jitter height
            **kwargs: Additional parameters

        Returns:
            New ggplot object with jittered points layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "shape": shape,
                "size": size,
                "stroke": stroke,
                "width": width,
                "height": height,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "jitter",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_density(
        self,
        mapping: Optional["aes"] = None,
        data: Optional[Any] = None,
        stat: str = "density",
        position: str = "identity",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        adjust: Optional[float] = 1,
        kernel: str = "gaussian",
        n: int = 512,
        trim: bool = False,
        **kwargs,
    ):
        """
        Add a density plot layer to the plot.

        Args:
            mapping: Aesthetic mappings
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Line color
            fill: Fill color
            linetype: Line type
            size: Line size
            adjust: Bandwidth adjustment
            kernel: Kernel to use
            n: Number of points for density estimation
            trim: Whether to trim density to data range
            **kwargs: Additional parameters

        Returns:
            New ggplot object with density layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "linetype": linetype,
                "size": size,
                "adjust": adjust,
                "kernel": kernel,
                "n": n,
                "trim": trim,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "density",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_area(
        self,
        mapping: Optional["aes"] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "stack",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Add an area plot layer to the plot.

        Args:
            mapping: Aesthetic mappings
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Outline color
            fill: Fill color
            linetype: Outline line type
            size: Outline line size
            **kwargs: Additional parameters

        Returns:
            New ggplot object with area layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "area",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_path(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Connect observations in the order they appear in the data.

        geom_path() connects the observations in the order in which they appear
        in the data. geom_line() connects them in order of the variable on the x axis.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation ("identity")
            position: Position adjustment ("identity")
            alpha: Transparency (0-1)
            color/colour: Line color
            linetype: Line type (solid, dashed, dotted, etc.)
            size: Line thickness
            **kwargs: Additional parameters

        Returns:
            New ggplot object with path layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "path",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_count(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "sum",
        position: str = "identity",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        shape: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Sum unique values. This is a variant of geom_point() that counts
        the number of observations at each location.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation ("sum")
            position: Position adjustment ("identity")
            alpha: Transparency (0-1)
            color/colour: Point outline color
            fill: Point fill color
            shape: Point shape
            size: Point size (or mapping based on count)
            **kwargs: Additional parameters

        Returns:
            New ggplot object with count layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "shape": shape,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "count",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_tile(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        **kwargs,
    ):
        """
        Display rectangles with x, y values mapped to the center of the tile.

        geom_tile() uses the center of the tile and its size (x, y, width, height).
        Useful for heatmaps and tiled visualizations.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Layer-specific data
            stat: Statistical transformation ("identity")
            position: Position adjustment ("identity")
            alpha: Transparency (0-1)
            color/colour: Tile outline color
            fill: Tile fill color
            linetype: Outline line type
            size: Outline line thickness
            width: Tile width
            height: Tile height
            **kwargs: Additional parameters

        Returns:
            New ggplot object with tile layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "fill": fill,
                "linetype": linetype,
                "size": size,
                "width": width,
                "height": height,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "tile",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_errorbar(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        alpha: Optional[float] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        linetype: Optional[Union[int, str]] = None,
        size: Optional[float] = None,
        width: Optional[float] = None,
        **kwargs,
    ):
        """
        Display error bars defined by the upper and lower values.

        Args:
            mapping: Aesthetic mappings for this layer (requires ymin, ymax)
            data: Layer-specific data
            stat: Statistical transformation ("identity")
            position: Position adjustment ("identity", "dodge")
            alpha: Transparency (0-1)
            color/colour: Error bar color
            linetype: Line type
            size: Line thickness
            width: Error bar cap width
            **kwargs: Additional parameters

        Returns:
            New ggplot object with errorbar layer added
        """
        new_plot = self._copy()

        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        params = {
            k: v
            for k, v in {
                "alpha": alpha,
                "color": color,
                "linetype": linetype,
                "size": size,
                "width": width,
                **kwargs,
            }.items()
            if v is not None
        }

        layer = {
            "geom_type": "errorbar",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }

        new_plot.layers.append(layer)
        return new_plot

    def geom_lollipop(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Draw lollipop chart (stick + point).
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "lollipop",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_pie(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        fill: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Draw pie chart.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "pie",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_dotplot(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        fill: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Dotplot: individual observations as dots.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "dotplot",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_bin2d(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "bin2d",
        position: str = "identity",
        fill: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        bins: Optional[int] = None,
        **kwargs,
    ):
        """
        2D rectangular binning (heatmap).
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "bins": bins,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "bin2d",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_hex(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "hex",
        position: str = "identity",
        fill: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        bins: Optional[int] = None,
        **kwargs,
    ):
        """
        Hexagonal binning.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "bins": bins,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "hex",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_raster(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        fill: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        **kwargs,
    ):
        """
        Raster/heatmap.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"fill": fill, "color": color, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "raster",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_crossbar(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        fill: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        width: Optional[float] = None,
        fatten: Optional[float] = None,
        **kwargs,
    ):
        """
        Crossbar: bar with horizontal median line.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "width": width,
                "fatten": fatten,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "crossbar",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_linerange(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Linerange: vertical line from ymin to ymax.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "linerange",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_pointrange(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        **kwargs,
    ):
        """
        Pointrange: vertical line with midpoint.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "pointrange",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_contour(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "contour",
        position: str = "identity",
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        bins: Optional[int] = None,
        **kwargs,
    ):
        """
        Contour lines of a 3D surface in 2D.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "color": color,
                "size": size,
                "bins": bins,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "contour",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_contourf(
        self,
        mapping=None,
        data=None,
        stat="contourf",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        bins=None,
        **kwargs,
    ):
        """Filled contours of a 3D surface in 2D."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "bins": bins,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "contourf",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_polygon(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Filled closed path defined by vertex coordinates."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "polygon",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_map(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Display polygons from a reference map."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "map",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_abline(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        slope=None,
        intercept=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Add a straight line with specified slope and intercept."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "slope": slope,
                "intercept": intercept,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "abline",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_hline(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        yintercept=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Add a straight horizontal line."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "yintercept": yintercept,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "hline",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_vline(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        xintercept=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Add a straight vertical line."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "xintercept": xintercept,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "vline",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_band(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Add a straight vertical or horizontal band."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "band",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_ribbon(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Display a y interval defined by ymin and ymax."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "ribbon",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_density2d(
        self,
        mapping=None,
        data=None,
        stat="density2d",
        position="identity",
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Display density function contour."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "density2d",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_density2df(
        self,
        mapping=None,
        data=None,
        stat="density2df",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        **kwargs,
    ):
        """Fill density function contour."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"fill": fill, "color": color, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "density2df",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_freqpoly(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Frequency polygon (line chart for counts)."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "freqpoly",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_step(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        direction=None,
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Step plot (stairs)."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "direction": direction,
                "color": color,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "step",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_rect(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Axis-aligned rectangle defined by two corners."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "rect",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_segment(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Draw a straight line segment between two points."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "segment",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_curve(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        curvature=None,
        color=None,
        colour=None,
        linetype=None,
        size=None,
        **kwargs,
    ):
        """Draw a curved line."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "curvature": curvature,
                "color": color,
                "linetype": linetype,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "curve",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_spoke(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        angle=None,
        radius=None,
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """
        Draw a straight line segment with given length and angle from the starting
        point.
        """
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "angle": angle,
                "radius": radius,
                "color": color,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "spoke",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_text_repel(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Add repelling text labels that avoid overlapping."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "text_repel",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_label(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Add a text with a rectangle behind the text."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "label",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_label_repel(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        fill=None,
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Add repelling text labels with background boxes."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "size": size,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "label_repel",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_qq(
        self,
        mapping=None,
        data=None,
        stat="qq",
        position="identity",
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Quantile-quantile plot."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "qq",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_qq2(
        self,
        mapping=None,
        data=None,
        stat="qq2",
        position="identity",
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Quantile-quantile plot (type 2)."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "qq2",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_qq_line(
        self,
        mapping=None,
        data=None,
        stat="qq_line",
        position="identity",
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Quantile-quantile fitting line."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "qq_line",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_qq2_line(
        self,
        mapping=None,
        data=None,
        stat="qq2_line",
        position="identity",
        color=None,
        colour=None,
        size=None,
        **kwargs,
    ):
        """Quantile-quantile fitting line (type 2)."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {"color": color, "size": size, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "qq2_line",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_function(
        self,
        mapping=None,
        data=None,
        stat="function",
        position="identity",
        color=None,
        colour=None,
        size=None,
        fun=None,
        **kwargs,
    ):
        """Compute and draw a function."""
        new_plot = self._copy()
        if color is None and colour is not None:
            color = colour
        params = {
            k: v
            for k, v in {
                "color": color,
                "size": size,
                "fun": fun,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": "function",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_blank(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        **kwargs,
    ):
        """Draw nothing (useful for scale expansion)."""
        new_plot = self._copy()
        params = {k: v for k, v in {**kwargs}.items() if v is not None}
        layer = {
            "geom_type": "blank",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_imshow(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        image=None,
        **kwargs,
    ):
        """Display image specified by ndarray with shape."""
        new_plot = self._copy()
        params = {k: v for k, v in {"image": image, **kwargs}.items() if v is not None}
        layer = {
            "geom_type": "imshow",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def geom_livemap(
        self,
        mapping=None,
        data=None,
        stat="identity",
        position="identity",
        location=None,
        zoom=None,
        **kwargs,
    ):
        """Display an interactive map."""
        new_plot = self._copy()
        params = {
            k: v
            for k, v in {"location": location, "zoom": zoom, **kwargs}.items()
            if v is not None
        }
        layer = {
            "geom_type": "livemap",
            "mapping": mapping,
            "data": data,
            "stat": stat,
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def stat_sum(
        self,
        mapping=None,
        data=None,
        geom="bar",
        position="identity",
        **kwargs,
    ):
        """Sum unique values (stat_sum)."""
        new_plot = self._copy()
        layer = {
            "geom_type": geom,
            "mapping": mapping,
            "data": data,
            "stat": "sum",
            "position": position,
            "params": {**kwargs},
        }
        new_plot.layers.append(layer)
        return new_plot

    def stat_summary(
        self,
        mapping=None,
        data=None,
        geom="pointrange",
        position="identity",
        fun_data=None,
        fun_y=None,
        fun_ymin=None,
        fun_ymax=None,
        **kwargs,
    ):
        """
        Aggregated values of a single continuous variable grouped along x
        (stat_summary).
        """
        new_plot = self._copy()
        params = {
            k: v
            for k, v in {
                "fun.data": fun_data,
                "fun.y": fun_y,
                "fun.ymin": fun_ymin,
                "fun.ymax": fun_ymax,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": geom,
            "mapping": mapping,
            "data": data,
            "stat": "summary",
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def stat_summary_bin(
        self,
        mapping=None,
        data=None,
        geom="pointrange",
        position="identity",
        bins=None,
        fun_data=None,
        fun_y=None,
        fun_ymin=None,
        fun_ymax=None,
        **kwargs,
    ):
        """Distribution by dividing x into bins and aggregating (stat_summary_bin)."""
        new_plot = self._copy()
        params = {
            k: v
            for k, v in {
                "bins": bins,
                "fun.data": fun_data,
                "fun.y": fun_y,
                "fun.ymin": fun_ymin,
                "fun.ymax": fun_ymax,
                **kwargs,
            }.items()
            if v is not None
        }
        layer = {
            "geom_type": geom,
            "mapping": mapping,
            "data": data,
            "stat": "summary_bin",
            "position": position,
            "params": params,
        }
        new_plot.layers.append(layer)
        return new_plot

    def stat_ecdf(
        self,
        mapping=None,
        data=None,
        geom="step",
        position="identity",
        **kwargs,
    ):
        """Empirical cumulative distribution function (stat_ecdf)."""
        new_plot = self._copy()
        layer = {
            "geom_type": geom,
            "mapping": mapping,
            "data": data,
            "stat": "ecdf",
            "position": position,
            "params": {**kwargs},
        }
        new_plot.layers.append(layer)
        return new_plot

    def arrow(self, angle=30, length=1, ends="last", type="open", **kwargs):
        """Describe arrows to add to a line (for use in geom_segment/curve)."""
        return {
            "arrow": {
                "angle": angle,
                "length": length,
                "ends": ends,
                "type": type,
                **kwargs,
            }
        }

    def expand_limits(self, x=None, y=None):
        """Expand the plot limits to include additional data values."""
        new_plot = self._copy()
        if not hasattr(new_plot, "limits"):
            new_plot.limits = {}
        if x is not None:
            new_plot.limits["x"] = x
        if y is not None:
            new_plot.limits["y"] = y
        return new_plot

    def as_discrete(self, column, order=None):
        """Convert a column to a discrete scale and specify order."""
        # This is a utility, not a layer; returns a tuple for mapping
        return (column, {"as_discrete": True, "order": order})

    def layer_labels(self, **kwargs):
        """Configure annotations for geometry layers."""
        new_plot = self._copy()
        if not hasattr(new_plot, "layer_labels"):
            new_plot.layer_labels = {}
        new_plot.layer_labels.update(kwargs)
        return new_plot

    def facet_grid(self, rows=None, cols=None, scales="fixed"):
        """Split data by one or two faceting variables (facet_grid)."""
        new_plot = self._copy()
        new_plot.facet = {
            "type": "grid",
            "rows": rows,
            "cols": cols,
            "scales": scales,
        }
        return new_plot

    def facet_wrap(self, facets=None, nrow=None, ncol=None, scales="fixed"):
        """Split data by one or more faceting variables (facet_wrap)."""
        new_plot = self._copy()
        new_plot.facet = {
            "type": "wrap",
            "facets": facets,
            "nrow": nrow,
            "ncol": ncol,
            "scales": scales,
        }
        return new_plot

    # ========================================================================
    # LABELS AND ANNOTATIONS
    # ========================================================================

    def labs(
        self,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        caption: Optional[str] = None,
        x: Optional[str] = None,
        y: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        fill: Optional[str] = None,
        size: Optional[str] = None,
        shape: Optional[str] = None,
        alpha: Optional[str] = None,
        linetype: Optional[str] = None,
        **kwargs,
    ):
        """
        Add labels to the plot.

        Args:
            title: Plot title
            subtitle: Plot subtitle
            caption: Plot caption
            x: X-axis label
            y: Y-axis label
            color/colour: Color scale label
            fill: Fill scale label
            size: Size scale label
            shape: Shape scale label
            alpha: Alpha scale label
            linetype: Linetype scale label
            **kwargs: Additional aesthetic labels

        Returns:
            New ggplot object with labels added
        """
        new_plot = self._copy()

        # Main plot labels
        if title is not None:
            new_plot.labels["title"] = title
        if subtitle is not None:
            new_plot.labels["subtitle"] = subtitle
        if caption is not None:
            new_plot.labels["caption"] = caption

        # Axis labels
        if x is not None:
            new_plot.labels["x"] = x
        if y is not None:
            new_plot.labels["y"] = y

        # Aesthetic labels - handle color/colour compatibility
        color_label = color if color is not None else colour
        if color_label is not None:
            new_plot.labels["color"] = color_label

        if fill is not None:
            new_plot.labels["fill"] = fill
        if size is not None:
            new_plot.labels["size"] = size
        if shape is not None:
            new_plot.labels["shape"] = shape
        if alpha is not None:
            new_plot.labels["alpha"] = alpha
        if linetype is not None:
            new_plot.labels["linetype"] = linetype

        # Additional labels from kwargs
        for key, value in kwargs.items():
            if value is not None:
                new_plot.labels[key] = value

        return new_plot

    def xlab(self, label: str):
        """Set x-axis label."""
        return self.labs(x=label)

    def ylab(self, label: str):
        """Set y-axis label."""
        return self.labs(y=label)

    def ggtitle(self, label: str, subtitle: Optional[str] = None):
        """Set plot title and optional subtitle."""
        return self.labs(title=label, subtitle=subtitle)

    # ========================================================================
    # FACETS AND COORDINATES
    # ========================================================================

    def coord_cartesian(
        self,
        xlim: Optional[tuple] = None,
        ylim: Optional[tuple] = None,
        expand: bool = True,
    ):
        """
        Set Cartesian coordinates / limits for the plot.

        Args:
            xlim: Tuple (xmin, xmax) or None.
            ylim: Tuple (ymin, ymax) or None.
            expand: Whether to expand the ranges.

        Returns:
            New ggplot object with coordinate settings applied.
        """
        new_plot = self._copy()
        coord = {
            "type": "cartesian",
            "xlim": xlim,
            "ylim": ylim,
            "expand": expand,
        }
        new_plot.coords = coord
        return new_plot

    def coord_flip(
        self,
        xlim: Optional[tuple] = None,
        ylim: Optional[tuple] = None,
        expand: bool = True,
    ):
        """
        Flip x and y axes.

        This coordinate system flips the x and y axes so that horizontal
        becomes vertical and vice versa. Useful for creating horizontal
        bar charts or when you have long axis labels.

        Args:
            xlim: Tuple (xmin, xmax) or None (applied after flipping)
            ylim: Tuple (ymin, ymax) or None (applied after flipping)
            expand: Whether to expand the ranges

        Returns:
            New ggplot object with flipped coordinates

        Examples:
            .coord_flip()  # Simple flip
            .coord_flip(xlim=(0, 100))  # Flip with limits
        """
        new_plot = self._copy()
        coord = {"type": "flip", "xlim": xlim, "ylim": ylim, "expand": expand}
        new_plot.coords = coord
        return new_plot

    # ========================================================================
    # THEMES
    # ========================================================================

    def theme_minimal(self, **kwargs):
        """
        Apply minimal theme.

        A minimalistic theme without axes lines. Only displays data and axes labels.

        Args:
            **kwargs: Additional theme customizations

        Returns:
            New ggplot object with minimal theme applied
        """
        from .themes import theme_minimal

        new_plot = self._copy()
        new_plot.theme = theme_minimal(**kwargs)
        return new_plot

    def theme_bw(self, **kwargs):
        """
        Apply black and white theme.

        Grey lines on white background with dark grey plot border.

        Args:
            **kwargs: Additional theme customizations

        Returns:
            New ggplot object with black and white theme applied
        """
        from .themes import theme_bw

        new_plot = self._copy()
        new_plot.theme = theme_bw(**kwargs)
        return new_plot

    def theme_classic(self, **kwargs):
        """
        Apply classic theme.

        Dark grey axes and no gridlines. Clean appearance like base R plots.

        Args:
            **kwargs: Additional theme customizations

        Returns:
            New ggplot object with classic theme applied
        """
        from .themes import theme_classic

        new_plot = self._copy()
        new_plot.theme = theme_classic(**kwargs)
        return new_plot

    def theme_grey(self, **kwargs):
        """
        Apply grey theme (default ggplot2 theme).

        Grey background and white gridlines.

        Args:
            **kwargs: Additional theme customizations

        Returns:
            New ggplot object with grey theme applied
        """
        from .themes import theme_grey

        new_plot = self._copy()
        new_plot.theme = theme_grey(**kwargs)
        return new_plot

    def theme_light(self, **kwargs):
        """
        Apply light theme.

        Light grey lines of various widths on white background.

        Args:
            **kwargs: Additional theme customizations

        Returns:
            New ggplot object with light theme applied
        """
        from .themes import theme_light

        new_plot = self._copy()
        new_plot.theme = theme_light(**kwargs)
        return new_plot

    def theme_void(self, **kwargs):
        """
        Apply void theme.

        Completely blank background: no borders, axes, or gridlines.

        Args:
            **kwargs: Additional theme customizations

        Returns:
            New ggplot object with void theme applied
        """
        from .themes import theme_void

        new_plot = self._copy()
        new_plot.theme = theme_void(**kwargs)
        return new_plot

    def theme(self, **kwargs):
        """
        Customize theme elements.

        Use theme() to modify individual components of a theme.

        Args:
            **kwargs: Theme properties (axis_title, legend_position, etc.)

        Returns:
            New ggplot object with custom theme applied

        Examples:
            .theme(legend_position='none')
            .theme(axis_title=element_text(size=14))
        """
        from .themes import theme

        new_plot = self._copy()
        new_plot.theme = theme(**kwargs)
        return new_plot

    # ========================================================================
    # SCALES
    # ========================================================================

    def scale_color_manual(
        self,
        values,
        name=None,
        breaks=None,
        labels=None,
        limits=None,
        guide=None,
        **kwargs,
    ):
        """
        Create a manual color scale for discrete data.

        Args:
            values: List of colors or dict mapping data values to colors.
            name: Name of the scale (legend title).
            breaks: Control which values appear as legend keys.
            labels: Labels for legend keys.
            limits: Data range for the scale.
            guide: Type of legend ('legend', 'colorbar', or 'none').
            **kwargs: Additional scale parameters.

        Returns:
            New ggplot object with color scale applied.

        Examples:
            .scale_color_manual(['red', 'blue', 'green'])
            .scale_color_manual({'A': 'red', 'B': 'blue'})
        """
        from .scales import scale_color_manual

        new_plot = self._copy()
        scale = scale_color_manual(
            values,
            name=name,
            breaks=breaks,
            labels=labels,
            limits=limits,
            guide=guide,
            **kwargs,
        )
        new_plot.scales["color"] = scale
        return new_plot

    def scale_fill_manual(
        self,
        values,
        name=None,
        breaks=None,
        labels=None,
        limits=None,
        guide=None,
        **kwargs,
    ):
        """
        Create a manual fill scale for discrete data.

        Args:
            values: List of colors or dict mapping data values to colors.
            name: Name of the scale (legend title).
            breaks: Control which values appear as legend keys.
            labels: Labels for legend keys.
            limits: Data range for the scale.
            guide: Type of legend ('legend', 'colorbar', or 'none').
            **kwargs: Additional scale parameters.

        Returns:
            New ggplot object with fill scale applied.

        Examples:
            .scale_fill_manual(['lightblue', 'lightgreen'])
            .scale_fill_manual({'Type1': 'lightblue', 'Type2': 'lightgreen'})
        """
        from .scales import scale_fill_manual

        new_plot = self._copy()
        scale = scale_fill_manual(
            values,
            name=name,
            breaks=breaks,
            labels=labels,
            limits=limits,
            guide=guide,
            **kwargs,
        )
        new_plot.scales["fill"] = scale
        return new_plot

    def scale_color_gradient(
        self,
        low="#132B43",
        high="#56B1F7",
        name=None,
        breaks=None,
        labels=None,
        limits=None,
        guide=None,
        **kwargs,
    ):
        """
        Create a two-color gradient scale for continuous color data.

        Args:
            low: Color for low values (default: dark blue).
            high: Color for high values (default: light blue).
            name: Name of the scale (legend title).
            breaks: Control which values appear as legend keys.
            labels: Labels for legend keys.
            limits: Data range for the scale.
            guide: Type of legend ('legend', 'colorbar', or 'none').
            **kwargs: Additional scale parameters.

        Returns:
            New ggplot object with color gradient scale applied.

        Examples:
            .scale_color_gradient()
            .scale_color_gradient(low='red', high='yellow')
        """
        from .scales import scale_color_gradient

        new_plot = self._copy()
        scale = scale_color_gradient(
            low=low,
            high=high,
            name=name,
            breaks=breaks,
            labels=labels,
            limits=limits,
            guide=guide,
            **kwargs,
        )
        new_plot.scales["color"] = scale
        return new_plot

    def scale_fill_gradient(
        self,
        low="#132B43",
        high="#56B1F7",
        name=None,
        breaks=None,
        labels=None,
        limits=None,
        guide=None,
        **kwargs,
    ):
        """
        Create a two-color gradient scale for continuous fill data.

        Args:
            low: Color for low values (default: dark blue).
            high: Color for high values (default: light blue).
            name: Name of the scale (legend title).
            breaks: Control which values appear as legend keys.
            labels: Labels for legend keys.
            limits: Data range for the scale.
            guide: Type of legend ('legend', 'colorbar', or 'none').
            **kwargs: Additional scale parameters.

        Returns:
            New ggplot object with fill gradient scale applied.

        Examples:
            .scale_fill_gradient()
            .scale_fill_gradient(low='lightgreen', high='darkgreen')
        """
        from .scales import scale_fill_gradient

        new_plot = self._copy()
        scale = scale_fill_gradient(
            low=low,
            high=high,
            name=name,
            breaks=breaks,
            labels=labels,
            limits=limits,
            guide=guide,
            **kwargs,
        )
        new_plot.scales["fill"] = scale
        return new_plot

    # ========================================================================
    # PLOT BUILDING AND RENDERING
    # ========================================================================

    def build(self) -> Dict[str, Any]:
        """
        Build the plot specification that can be sent to lets-plot.

        Returns:
            Dictionary containing the complete plot specification
        """
        spec = {
            "kind": "plot",
            "data": self._prepare_data(),
            "mapping": self._prepare_mapping(),
            "layers": self._prepare_layers(),
            "scales": self._prepare_scales(),
            "labels": self.labels,
            "theme": self.theme,
        }

        if self.coords:
            spec["coord"] = self.coords

        if self.facets:
            spec["facet"] = self.facets

        return spec

    def _prepare_data(self) -> Dict[str, List]:
        """Convert pandas DataFrame to dict format expected by lets-plot."""
        if self.data is None:
            return {}

        # If data is already a dict, return it as-is
        if isinstance(self.data, dict):
            return self.data

        # If pandas not available, can't handle other data types
        if not HAS_PANDAS:
            return {}

        # Handle pandas DataFrame
        if hasattr(self.data, "columns"):
            data_dict = {}
            for col in self.data.columns:
                series = self.data[col]

                # Convert various data types to JSON-serializable formats
                if pd.api.types.is_numeric_dtype(series):
                    # Handle NaN values
                    values = series.fillna("null").tolist()
                    # Convert numpy types to native Python types
                    data_dict[col] = [
                        (float(x) if x != "null" and not np.isnan(float(x)) else None)
                        for x in values
                    ]
                elif pd.api.types.is_datetime64_any_dtype(series):
                    data_dict[col] = series.dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
                else:
                    data_dict[col] = series.astype(str).tolist()

            return data_dict

        # Fallback: unknown data type
        return {}

    def _prepare_mapping(self) -> Dict[str, str]:
        """Prepare the default aesthetic mappings."""
        if self.mapping is None:
            return {}
        return self.mapping.mapping

    def _prepare_layers(self) -> List[Dict[str, Any]]:
        """Prepare all layers for the plot specification."""
        layers = []
        for layer in self.layers:
            layer_spec = {
                "geom": layer["geom_type"],
                "stat": layer.get("stat", "identity"),
                "position": layer.get("position", "identity"),
                "mapping": (layer["mapping"].mapping if layer["mapping"] else {}),
                "params": layer["params"],
            }

            if layer.get("data") is not None:
                layer_spec["data"] = self._prepare_layer_data(layer["data"])

            layers.append(layer_spec)

        return layers

    def _prepare_layer_data(self, data: Any) -> Dict[str, List]:
        """Prepare data for a specific layer."""
        return (
            self._prepare_data() if data is self.data else self._convert_dataframe(data)
        )

    def _convert_dataframe(self, df: Any) -> Dict[str, List]:
        """Convert any DataFrame to lets-plot format."""
        # If data is already a dict, return it as-is
        if isinstance(df, dict):
            return df

        # If pandas not available, can't handle other data types
        if not HAS_PANDAS:
            return {}

        # Handle pandas DataFrame
        if hasattr(df, "columns"):
            data_dict = {}
            for col in df.columns:
                series = df[col]
                if pd.api.types.is_numeric_dtype(series):
                    data_dict[col] = series.fillna(None).tolist()
                else:
                    data_dict[col] = series.astype(str).tolist()
            return data_dict

        # Fallback: unknown data type
        return {}

    def _prepare_scales(self) -> List[Dict[str, Any]]:
        """Prepare scale specifications."""
        scales = []
        for aesthetic, scale in self.scales.items():
            scale_spec = {"aesthetic": aesthetic, "type": scale.scale_type}

            # Add all scale attributes dynamically
            for attr in [
                "name",
                "breaks",
                "labels",
                "limits",
                "transform",
                "guide",
                "values",
                "low",
                "high",
            ]:
                value = getattr(scale, attr, None)
                if value is not None:
                    scale_spec[attr] = value

            scales.append(scale_spec)
        return scales

    def show(self):
        """Render and display the plot."""
        spec = self.build()
        return self.bridge.render_plot(spec)

    def save(
        self,
        filename: str,
        width: int = 600,
        height: int = 400,
        format: str = "html",
    ):
        """
        Save the plot to a file.

        Args:
            filename: Output filename
            width: Plot width in pixels
            height: Plot height in pixels
            format: Output format ('html', 'png', 'svg')
        """
        spec = self.build()
        return self.bridge.save_plot(spec, filename, width, height, format)

    def _repr_html_(self):
        """Jupyter notebook representation."""
        return self.show()
