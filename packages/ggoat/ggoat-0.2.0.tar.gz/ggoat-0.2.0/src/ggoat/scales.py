from typing import Dict, List, Optional, Union


# Position scales
def scale_x_discrete(**kwargs):
    return Scale("x", "discrete", **kwargs)


def scale_y_discrete(**kwargs):
    return Scale("y", "discrete", **kwargs)


def scale_x_discrete_reversed(**kwargs):
    return Scale("x", "discrete_reversed", **kwargs)


def scale_y_discrete_reversed(**kwargs):
    return Scale("y", "discrete_reversed", **kwargs)


def scale_x_continuous(**kwargs):
    return Scale("x", "continuous", **kwargs)


def scale_y_continuous(**kwargs):
    return Scale("y", "continuous", **kwargs)


def scale_x_log10(**kwargs):
    return Scale("x", "log10", transform="log10", **kwargs)


def scale_y_log10(**kwargs):
    return Scale("y", "log10", transform="log10", **kwargs)


def scale_x_log2(**kwargs):
    return Scale("x", "log2", transform="log2", **kwargs)


def scale_y_log2(**kwargs):
    return Scale("y", "log2", transform="log2", **kwargs)


def scale_x_reverse(**kwargs):
    return Scale("x", "reverse", transform="reverse", **kwargs)


def scale_y_reverse(**kwargs):
    return Scale("y", "reverse", transform="reverse", **kwargs)


# Color/fill scales (ajouts)
def scale_color_gradient2(
    low="#132B43", mid="#FFFFFF", high="#56B1F7", midpoint=0, **kwargs
):
    return Scale(
        "color",
        "gradient2",
        low=low,
        mid=mid,
        high=high,
        midpoint=midpoint,
        **kwargs,
    )


def scale_fill_gradient2(
    low="#132B43", mid="#FFFFFF", high="#56B1F7", midpoint=0, **kwargs
):
    return Scale(
        "fill",
        "gradient2",
        low=low,
        mid=mid,
        high=high,
        midpoint=midpoint,
        **kwargs,
    )


def scale_color_gradientn(colors=None, **kwargs):
    return Scale("color", "gradientn", colors=colors, **kwargs)


def scale_fill_gradientn(colors=None, **kwargs):
    return Scale("fill", "gradientn", colors=colors, **kwargs)


def scale_color_hue(**kwargs):
    return Scale("color", "hue", **kwargs)


def scale_fill_hue(**kwargs):
    return Scale("fill", "hue", **kwargs)


def scale_color_discrete(**kwargs):
    return Scale("color", "discrete", **kwargs)


def scale_fill_discrete(**kwargs):
    return Scale("fill", "discrete", **kwargs)


def scale_color_grey(**kwargs):
    return Scale("color", "grey", **kwargs)


def scale_fill_grey(**kwargs):
    return Scale("fill", "grey", **kwargs)


def scale_color_brewer(type="seq", palette=None, **kwargs):
    return Scale("color", "brewer", type=type, palette=palette, **kwargs)


def scale_fill_brewer(type="seq", palette=None, **kwargs):
    return Scale("fill", "brewer", type=type, palette=palette, **kwargs)


def scale_color_viridis(option="D", **kwargs):
    return Scale("color", "viridis", option=option, **kwargs)


def scale_fill_viridis(option="D", **kwargs):
    return Scale("fill", "viridis", option=option, **kwargs)


def scale_color_cmapmpl(cmap=None, **kwargs):
    return Scale("color", "cmapmpl", cmap=cmap, **kwargs)


def scale_fill_cmapmpl(cmap=None, **kwargs):
    return Scale("fill", "cmapmpl", cmap=cmap, **kwargs)


# Flexible scales
def scale_manual(aesthetic, values, **kwargs):
    return ManualScale(aesthetic, values, **kwargs)


def scale_continuous(aesthetic, **kwargs):
    return Scale(aesthetic, "continuous", **kwargs)


def scale_discrete(aesthetic, **kwargs):
    return Scale(aesthetic, "discrete", **kwargs)


def scale_gradient(aesthetic, low="#132B43", high="#56B1F7", **kwargs):
    return Scale(aesthetic, "gradient", low=low, high=high, **kwargs)


def scale_gradient2(
    aesthetic,
    low="#132B43",
    mid="#FFFFFF",
    high="#56B1F7",
    midpoint=0,
    **kwargs,
):
    return Scale(
        aesthetic,
        "gradient2",
        low=low,
        mid=mid,
        high=high,
        midpoint=midpoint,
        **kwargs,
    )


def scale_gradientn(aesthetic, colors=None, **kwargs):
    return Scale(aesthetic, "gradientn", colors=colors, **kwargs)


def scale_hue(aesthetic, **kwargs):
    return Scale(aesthetic, "hue", **kwargs)


def scale_grey(aesthetic, **kwargs):
    return Scale(aesthetic, "grey", **kwargs)


def scale_brewer(aesthetic, type="seq", palette=None, **kwargs):
    return Scale(aesthetic, "brewer", type=type, palette=palette, **kwargs)


def scale_viridis(aesthetic, option="D", **kwargs):
    return Scale(aesthetic, "viridis", option=option, **kwargs)


def scale_cmapmpl(aesthetic, cmap=None, **kwargs):
    return Scale(aesthetic, "cmapmpl", cmap=cmap, **kwargs)


# Shape/size/alpha/linetype
def scale_shape(**kwargs):
    return Scale("shape", "shape", **kwargs)


def scale_shape_manual(values, **kwargs):
    return ManualScale("shape", values, **kwargs)


def scale_size_manual(values, **kwargs):
    return ManualScale("size", values, **kwargs)


def scale_size(**kwargs):
    return Scale("size", "size", **kwargs)


def scale_size_area(**kwargs):
    return Scale("size", "size_area", **kwargs)


def scale_linewidth(**kwargs):
    return Scale("linewidth", "linewidth", **kwargs)


def scale_stroke(**kwargs):
    return Scale("stroke", "stroke", **kwargs)


def scale_alpha_manual(values, **kwargs):
    return ManualScale("alpha", values, **kwargs)


def scale_alpha(**kwargs):
    return Scale("alpha", "alpha", **kwargs)


def scale_linetype_manual(values, **kwargs):
    return ManualScale("linetype", values, **kwargs)


# Datetime scales
def scale_x_datetime(**kwargs):
    return Scale("x", "datetime", **kwargs)


def scale_y_datetime(**kwargs):
    return Scale("y", "datetime", **kwargs)


def scale_x_time(**kwargs):
    return Scale("x", "time", **kwargs)


def scale_y_time(**kwargs):
    return Scale("y", "time", **kwargs)


# Identity scales
def scale_identity(aesthetic, **kwargs):
    return Scale(aesthetic, "identity", **kwargs)


def scale_color_identity(**kwargs):
    return Scale("color", "identity", **kwargs)


def scale_fill_identity(**kwargs):
    return Scale("fill", "identity", **kwargs)


def scale_shape_identity(**kwargs):
    return Scale("shape", "identity", **kwargs)


def scale_linetype_identity(**kwargs):
    return Scale("linetype", "identity", **kwargs)


def scale_alpha_identity(**kwargs):
    return Scale("alpha", "identity", **kwargs)


def scale_size_identity(**kwargs):
    return Scale("size", "identity", **kwargs)


def scale_linewidth_identity(**kwargs):
    return Scale("linewidth", "identity", **kwargs)


def scale_stroke_identity(**kwargs):
    return Scale("stroke", "identity", **kwargs)


# Scale limits
def lims(x=None, y=None):
    return {"lims": {"x": x, "y": y}}


def xlim(*args):
    return {"xlim": list(args)}


def ylim(*args):
    return {"ylim": list(args)}


# Scale guides
def guide_legend(**kwargs):
    return {"guide": "legend", **kwargs}


def guide_colorbar(**kwargs):
    return {"guide": "colorbar", **kwargs}


def guides(**kwargs):
    return {"guides": kwargs}


def layer_key(**kwargs):
    return {"layer_key": kwargs}


class Scale:
    """Base class for all scales."""

    def __init__(self, aesthetic: str, scale_type: str, **kwargs):
        self.aesthetic = aesthetic
        self.scale_type = scale_type
        self.name = kwargs.get("name")
        self.breaks = kwargs.get("breaks")
        self.labels = kwargs.get("labels")
        self.limits = kwargs.get("limits")
        self.transform = kwargs.get("transform")
        self.guide = kwargs.get("guide")

        # Store all additional parameters
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)


class ManualScale(Scale):
    """Manual scale for discrete aesthetics."""

    def __init__(self, aesthetic: str, values: Union[List, Dict], **kwargs):
        super().__init__(aesthetic, "manual", **kwargs)
        self.values = values


def scale_color_manual(
    values: Union[List[str], Dict[str, str]],
    name: Optional[str] = None,
    breaks: Optional[List] = None,
    labels: Optional[List[str]] = None,
    limits: Optional[List] = None,
    guide: Optional[str] = None,
    **kwargs,
) -> ManualScale:
    """
    Create a manual color scale for discrete data.

    Args:
        values: List of colors or dict mapping data values to colors.
                Colors can be hex codes ('#ff0000'), named colors ('red'),
                or RGB tuples.
        name: Name of the scale (legend title). If None, uses the aesthetic name.
        breaks: Control which values appear as legend keys.
        labels: Labels for legend keys.
        limits: Data range for the scale.
        guide: Type of legend ('legend', 'colorbar', or 'none').
        **kwargs: Additional scale parameters.

    Returns:
        ManualScale object for color aesthetic.

    Examples:
        # Using a list of colors
        .scale_color_manual(['red', 'blue', 'green'])

        # Using hex codes
        .scale_color_manual(['#ff0000', '#0000ff', '#00ff00'])

        # Using a mapping dict
        .scale_color_manual({'A': 'red', 'B': 'blue', 'C': 'green'})

        # With custom legend title
        .scale_color_manual(['red', 'blue'], name="Group Type")
    """
    return ManualScale(
        "color",
        values,
        name=name,
        breaks=breaks,
        labels=labels,
        limits=limits,
        guide=guide,
        **kwargs,
    )


def scale_fill_manual(
    values: Union[List[str], Dict[str, str]],
    name: Optional[str] = None,
    breaks: Optional[List] = None,
    labels: Optional[List[str]] = None,
    limits: Optional[List] = None,
    guide: Optional[str] = None,
    **kwargs,
) -> ManualScale:
    """
    Create a manual fill scale for discrete data.

    Args:
        values: List of colors or dict mapping data values to colors.
                Colors can be hex codes ('#ff0000'), named colors ('red'),
                or RGB tuples.
        name: Name of the scale (legend title). If None, uses the aesthetic name.
        breaks: Control which values appear as legend keys.
        labels: Labels for legend keys.
        limits: Data range for the scale.
        guide: Type of legend ('legend', 'colorbar', or 'none').
        **kwargs: Additional scale parameters.

    Returns:
        ManualScale object for fill aesthetic.

    Examples:
        # Using a list of colors
        .scale_fill_manual(['lightblue', 'lightgreen', 'lightcoral'])

        # Using hex codes with transparency
        .scale_fill_manual(['#ff000080', '#0000ff80', '#00ff0080'])

        # Using a mapping dict
        .scale_fill_manual({'Type1': 'lightblue', 'Type2': 'lightgreen'})

        # Remove legend
        .scale_fill_manual(['red', 'blue'], guide='none')
    """
    return ManualScale(
        "fill",
        values,
        name=name,
        breaks=breaks,
        labels=labels,
        limits=limits,
        guide=guide,
        **kwargs,
    )


def scale_color_gradient(
    low: str = "#132B43",
    high: str = "#56B1F7",
    name: Optional[str] = None,
    breaks: Optional[List] = None,
    labels: Optional[List[str]] = None,
    limits: Optional[List] = None,
    guide: Optional[str] = None,
    **kwargs,
) -> Scale:
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
        Scale object for continuous color aesthetic.

    Examples:
        # Default blue gradient
        .scale_color_gradient()

        # Custom red to yellow gradient
        .scale_color_gradient(low='red', high='yellow')

        # With custom range
        .scale_color_gradient(low='#000000', high='#ffffff', limits=[0, 100])
    """
    return Scale(
        "color",
        "gradient",
        low=low,
        high=high,
        name=name,
        breaks=breaks,
        labels=labels,
        limits=limits,
        guide=guide,
        **kwargs,
    )


def scale_fill_gradient(
    low: str = "#132B43",
    high: str = "#56B1F7",
    name: Optional[str] = None,
    breaks: Optional[List] = None,
    labels: Optional[List[str]] = None,
    limits: Optional[List] = None,
    guide: Optional[str] = None,
    **kwargs,
) -> Scale:
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
        Scale object for continuous fill aesthetic.

    Examples:
        # Default blue gradient
        .scale_fill_gradient()

        # Custom green gradient
        .scale_fill_gradient(low='lightgreen', high='darkgreen')
    """
    return Scale(
        "fill",
        "gradient",
        low=low,
        high=high,
        name=name,
        breaks=breaks,
        labels=labels,
        limits=limits,
        guide=guide,
        **kwargs,
    )
