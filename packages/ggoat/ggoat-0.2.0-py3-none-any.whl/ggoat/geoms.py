"""
Geometric objects (geoms) for ggplot.

Geoms are the visual elements used to represent data in a plot.
Each geom draws a particular type of plot element.
"""

from typing import Any, Optional, Union

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    pd = None
    HAS_PANDAS = False

from .aes import aes


class Geom:
    """
    Base class for all geometric objects.

    This class defines the interface that all geoms must implement
    and provides common functionality.
    """

    def __init__(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "identity",
        position: str = "identity",
        **kwargs,
    ):
        """
        Initialize a geometric object.

        Args:
            mapping: Aesthetic mappings for this layer
            data: Data for this layer (overrides plot data) - DataFrame or dict
            stat: Statistical transformation to use
            position: Position adjustment
            **kwargs: Additional parameters specific to the geom
        """
        self.mapping = mapping
        self.data = data
        self.stat = stat
        self.position = position
        self.params = kwargs
        self.component_type = "geom"

    def add_to_plot(self, plot):
        """Add this geom as a layer to a plot."""
        plot.layers.append(self)


class geom_point(Geom):
    """
    Scatter plot points.

    geom_point() understands the following aesthetics:
    - x (required)
    - y (required)
    - alpha
    - color
    - fill
    - shape
    - size
    - stroke
    """

    def __init__(
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
        Create point geometry.

        Args:
            mapping: Aesthetic mappings
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
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "point"


class geom_line(Geom):
    """
    Line plots.

    geom_line() understands the following aesthetics:
    - x (required)
    - y (required)
    - alpha
    - color
    - linetype
    - size
    - group
    """

    def __init__(
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
        Create line geometry.

        Args:
            mapping: Aesthetic mappings
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Line color
            linetype: Line type (solid, dashed, etc.)
            size: Line size/width
            **kwargs: Additional parameters
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "line"


class geom_bar(Geom):
    """
    Bar charts.

    geom_bar() understands the following aesthetics:
    - x (required for vertical bars)
    - y (required for horizontal bars)
    - alpha
    - color
    - fill
    - linetype
    - size
    - weight
    """

    def __init__(
        self,
        mapping: Optional[aes] = None,
        data: Optional[Any] = None,
        stat: str = "count",
        position: str = "stack",
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
        Create bar geometry.

        Args:
            mapping: Aesthetic mappings
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
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "bar"


class geom_histogram(Geom):
    """
    Histograms.

    geom_histogram() is a shortcut for geom_bar() with stat="bin".
    It understands the following aesthetics:
    - x (required)
    - alpha
    - color
    - fill
    - linetype
    - size
    - weight
    """

    def __init__(
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
        Create histogram geometry.

        Args:
            mapping: Aesthetic mappings
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
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "histogram"


class geom_smooth(Geom):
    """
    Smoothed conditional means.

    geom_smooth() understands the following aesthetics:
    - x (required)
    - y (required)
    - alpha
    - color
    - fill
    - linetype
    - size
    - weight
    """

    def __init__(
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
        Create smooth geometry.

        Args:
            mapping: Aesthetic mappings
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
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "smooth"


class geom_boxplot(Geom):
    """
    Box and whisker plots.

    geom_boxplot() understands the following aesthetics:
    - x (discrete) or y (continuous) - required
    - lower (for custom box plots)
    - upper (for custom box plots)
    - middle (for custom box plots)
    - ymin (for custom box plots)
    - ymax (for custom box plots)
    - alpha
    - color
    - fill
    - linetype
    - shape (for outliers)
    - size
    - weight
    """

    def __init__(
        self,
        mapping: Optional[aes] = None,
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
        Create boxplot geometry.

        Args:
            mapping: Aesthetic mappings
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            color/colour: Box outline color
            fill: Box fill color
            linetype: Outline line type
            size: Outline line size
            width: Box width
            outlier_alpha: Outlier point transparency
            outlier_color/outlier_colour: Outlier point color
            outlier_fill: Outlier point fill
            outlier_shape: Outlier point shape
            outlier_size: Outlier point size
            outlier_stroke: Outlier point stroke
            notch: Whether to draw notched boxes
            notchwidth: Relative width of notches
            varwidth: Whether to make box widths proportional to sqrt(n)
            **kwargs: Additional parameters
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "boxplot"


class geom_violin(Geom):
    """
    Violin plots.

    A violin plot is a mirrored density plot with an additional grouping as for a
    boxplot.

    geom_violin() understands the following aesthetics:
    - x (discrete) or y (continuous) - required
    - alpha
    - color
    - fill
    - linetype
    - size
    - weight
    """

    def __init__(
        self,
        mapping: Optional[aes] = None,
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
        Create violin plot geometry.

        Args:
            mapping: Aesthetic mappings
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
            draw_quantiles: Quantile lines to draw (e.g., [0.25, 0.5, 0.75])
            **kwargs: Additional parameters
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "violin"


class geom_text(Geom):
    """
    Text annotations.

    geom_text() understands the following aesthetics:
    - x (required)
    - y (required)
    - label (required)
    - alpha
    - angle
    - color
    - family
    - fontface
    - hjust
    - lineheight
    - size
    - vjust
    """

    def __init__(
        self,
        mapping: Optional[aes] = None,
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
        Create text geometry.

        Args:
            mapping: Aesthetic mappings (must include 'label')
            data: Layer-specific data
            stat: Statistical transformation
            position: Position adjustment
            alpha: Transparency (0-1)
            angle: Text angle in degrees
            color/colour: Text color
            family: Font family
            fontface: Font face ("plain", "bold", "italic", "bold.italic")
            hjust: Horizontal justification (0=left, 0.5=center, 1=right)
            lineheight: Line height multiplier
            size: Text size
            vjust: Vertical justification (0=bottom, 0.5=center, 1=top)
            check_overlap: Whether to check for overlapping text
            **kwargs: Additional parameters
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "text"


class geom_jitter(Geom):
    """
    Jittered points.

    Jittered points are useful for discrete plots or when points are stacked.
    This is a shortcut for geom_point() with position="jitter".

    geom_jitter() understands the following aesthetics:
    - x (required)
    - y (required)
    - alpha
    - color
    - fill
    - shape
    - size
    - stroke
    """

    def __init__(
        self,
        mapping: Optional[aes] = None,
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
        Create jittered point geometry.

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
            width: Jitter width (default: 40% of category width)
            height: Jitter height (default: 0)
            **kwargs: Additional parameters
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "jitter"


class geom_density(Geom):
    """
    Density plots.

    Kernel density estimation, which is a smoothed version of the histogram.

    geom_density() understands the following aesthetics:
    - x (required)
    - alpha
    - color
    - fill
    - linetype
    - size
    - weight
    """

    def __init__(
        self,
        mapping: Optional[aes] = None,
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
        Create density plot geometry.

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
            adjust: Bandwidth adjustment (multiply by this value)
            kernel: Kernel to use ("gaussian", "epanechnikov", "rectangular", etc.)
            n: Number of equally spaced points for density estimation
            trim: Whether to trim density to data range
            **kwargs: Additional parameters
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "density"


class geom_area(Geom):
    """
    Area plots.

    Display the development of quantitative values over an interval.

    geom_area() understands the following aesthetics:
    - x (required)
    - y (required)
    - alpha
    - color
    - fill
    - linetype
    - size
    - group
    """

    def __init__(
        self,
        mapping: Optional[aes] = None,
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
        Create area geometry.

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
        """
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

        super().__init__(mapping, data, stat, position, **params)
        self.geom_type = "area"
