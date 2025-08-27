"""
Theme system for customizing the overall appearance of plots.
"""

from typing import Optional, Union


class Theme:
    """Base class for all themes."""

    def __init__(self, **kwargs):
        """Initialize theme with custom properties."""
        self.properties = kwargs
        self.theme_type = "custom"


class PredefinedTheme(Theme):
    """Predefined theme with standard lets-plot theme name."""

    def __init__(self, theme_name: str, **kwargs):
        super().__init__(**kwargs)
        self.theme_name = theme_name
        self.theme_type = "predefined"


def theme_minimal(**kwargs) -> PredefinedTheme:
    """
    A minimalistic theme without axes lines.

    The most minimal theme with no background annotations.
    Only displays data and axes labels.

    Args:
        **kwargs: Additional theme customizations

    Returns:
        PredefinedTheme object for minimal theme

    Examples:
        .theme_minimal()
        .theme_minimal(text=element_text(size=12))
    """
    return PredefinedTheme("minimal", **kwargs)


def theme_bw(**kwargs) -> PredefinedTheme:
    """
    Black and white theme.

    Grey lines on white background with dark grey plot border.
    Classic theme suitable for publications.

    Args:
        **kwargs: Additional theme customizations

    Returns:
        PredefinedTheme object for black and white theme

    Examples:
        .theme_bw()
        .theme_bw(legend_position='bottom')
    """
    return PredefinedTheme("bw", **kwargs)


def theme_classic(**kwargs) -> PredefinedTheme:
    """
    Classic theme.

    Dark grey axes and no gridlines. Clean and simple appearance
    similar to base R plots.

    Args:
        **kwargs: Additional theme customizations

    Returns:
        PredefinedTheme object for classic theme

    Examples:
        .theme_classic()
        .theme_classic(strip_background=element_blank())
    """
    return PredefinedTheme("classic", **kwargs)


def theme_grey(**kwargs) -> PredefinedTheme:
    """
    Grey theme (default ggplot2 theme).

    Grey background and white gridlines. This is the default
    ggplot2 theme.

    Args:
        **kwargs: Additional theme customizations

    Returns:
        PredefinedTheme object for grey theme

    Examples:
        .theme_grey()
        .theme_grey(panel_grid_minor=element_blank())
    """
    return PredefinedTheme("grey", **kwargs)


def theme_light(**kwargs) -> PredefinedTheme:
    """
    Light theme.

    Light grey lines of various widths on white background.

    Args:
        **kwargs: Additional theme customizations

    Returns:
        PredefinedTheme object for light theme

    Examples:
        .theme_light()
    """
    return PredefinedTheme("light", **kwargs)


def theme_void(**kwargs) -> PredefinedTheme:
    """
    Void theme.

    A completely blank (or "void") background theme: no borders,
    axes, or gridlines. Useful for maps and specialized plots.

    Args:
        **kwargs: Additional theme customizations

    Returns:
        PredefinedTheme object for void theme

    Examples:
        .theme_void()
    """
    return PredefinedTheme("void", **kwargs)


# Theme elements for customization
class ThemeElement:
    """Base class for theme elements."""

    def __init__(self, **kwargs):
        self.properties = kwargs


class element_blank(ThemeElement):
    """Element that draws nothing and assigns no space."""

    def __init__(self):
        super().__init__(element_type="blank")


class element_text(ThemeElement):
    """Text element for theme customization."""

    def __init__(
        self,
        family: Optional[str] = None,
        face: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        hjust: Optional[float] = None,
        vjust: Optional[float] = None,
        angle: Optional[float] = None,
        lineheight: Optional[float] = None,
        **kwargs,
    ):
        """
        Create text theme element.

        Args:
            family: Font family
            face: Font face ("plain", "italic", "bold", "bold.italic")
            color/colour: Text color
            size: Text size
            hjust: Horizontal justification (0-1)
            vjust: Vertical justification (0-1)
            angle: Text angle in degrees
            lineheight: Line height multiplier
            **kwargs: Additional properties
        """
        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        properties = {
            k: v
            for k, v in {
                "family": family,
                "face": face,
                "color": color,
                "size": size,
                "hjust": hjust,
                "vjust": vjust,
                "angle": angle,
                "lineheight": lineheight,
                "element_type": "text",
                **kwargs,
            }.items()
            if v is not None
        }

        super().__init__(**properties)


class element_line(ThemeElement):
    """Line element for theme customization."""

    def __init__(
        self,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        linetype: Optional[Union[str, int]] = None,
        **kwargs,
    ):
        """
        Create line theme element.

        Args:
            color/colour: Line color
            size: Line size
            linetype: Line type
            **kwargs: Additional properties
        """
        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        properties = {
            k: v
            for k, v in {
                "color": color,
                "size": size,
                "linetype": linetype,
                "element_type": "line",
                **kwargs,
            }.items()
            if v is not None
        }

        super().__init__(**properties)


class element_rect(ThemeElement):
    """Rectangle element for theme customization."""

    def __init__(
        self,
        fill: Optional[str] = None,
        color: Optional[str] = None,
        colour: Optional[str] = None,
        size: Optional[float] = None,
        linetype: Optional[Union[str, int]] = None,
        **kwargs,
    ):
        """
        Create rectangle theme element.

        Args:
            fill: Fill color
            color/colour: Border color
            size: Border size
            linetype: Border line type
            **kwargs: Additional properties
        """
        # Handle color/colour compatibility
        if color is None and colour is not None:
            color = colour

        properties = {
            k: v
            for k, v in {
                "fill": fill,
                "color": color,
                "size": size,
                "linetype": linetype,
                "element_type": "rect",
                **kwargs,
            }.items()
            if v is not None
        }

        super().__init__(**properties)


def theme(**kwargs) -> Theme:
    """
    Create a custom theme or modify an existing theme.

    Use theme() to modify individual components of a theme, allowing you
    to control all non-data components of the plot.

    Args:
        **kwargs: Theme properties to set. Common properties include:
                 - axis_title: Axis title appearance
                 - axis_text: Axis text appearance
                 - plot_title: Plot title appearance
                 - legend_position: on "top", "bottom", "left", "right""none"
                 - panel_background: Panel background
                 - plot_background: Plot background
                 - panel_grid_major: Major grid lines
                 - panel_grid_minor: Minor grid lines

    Returns:
        Theme object with custom properties

    Examples:
        # Remove legend
        .theme(legend_position='none')

        # Customize text
        .theme(axis_title=element_text(size=14, face='bold'),
               plot_title=element_text(size=16, hjust=0.5))

        # Remove grid lines
        .theme(panel_grid_major=element_blank(),
               panel_grid_minor=element_blank())
    """
    return Theme(**kwargs)
