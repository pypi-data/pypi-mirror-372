"""
Position adjustments for overlapping objects.
"""

from typing import Optional


class Position:
    """Base class for position adjustments."""

    def __init__(self, position_type: str, **kwargs):
        self.position_type = position_type
        self.params = kwargs


def position_identity() -> Position:
    """
    Don't adjust position (default).

    Returns:
        Position object for identity positioning
    """
    return Position("identity")


def position_dodge(width: Optional[float] = None, preserve: str = "total") -> Position:
    """
    Adjust position by dodging overlaps to the side.

    Dodging preserves the vertical position of an geom while adjusting
    the horizontal position. Useful for bar charts and boxplots.

           params["width"] = width
        width: Dodging width, when different to the width of the individual
               elements. This is useful when you want to align narrow geoms
               with wider geoms.
        preserve: Should dodging preserve the "total" width of all elements
                 at a position, or the width of a "single" element?

    Returns:
        Position object for dodge positioning

    Examples:
        .geom_bar(position=position_dodge())
        .geom_boxplot(position=position_dodge(width=0.8))
    """
    params = {}
    if width is not None:
        params["width"] = width
    if preserve != "total":
        params["preserve"] = preserve

    return Position("dodge", **params)


def position_dodge2(
    width: Optional[float] = None,
    preserve: str = "total",
    padding: float = 0.1,
    reverse: bool = False,
) -> Position:
    """
    Adjust position by dodging overlaps to the side (enhanced version).

    position_dodge2() is a special case of position_dodge() for arranging
    box plots, which can have variable widths.

    Args:
        width: Dodging width
        preserve: Should dodging preserve the "total" width or "single" element width
        padding: Padding between elements
        reverse: If True, will reverse the default stacking order

    Returns:
        Position object for dodge2 positioning
    """
    params = {}
    if width is not None:
        params["width"] = width
    if preserve != "total":
        params["preserve"] = preserve
    if padding != 0.1:
        params["padding"] = float(padding)
    if reverse:
        params["reverse"] = reverse

    return Position("dodge2", **params)


def position_jitter(
    width: Optional[float] = None,
    height: Optional[float] = None,
    seed: Optional[int] = None,
) -> Position:
    """
    Adjust position by assigning random noise to points.

    Jittering is useful when you have a discrete variable on one axis and
    a continuous variable on the other, and many data points have the same
    discrete value.

    Args:
           params["width"] = width
               in both positive and negative directions, so the total spread
               is twice the value specified here.
        height: Amount of jitter in y direction (default: 0)
        seed: Random seed for reproducible jitter

    Returns:
        Position object for jitter positioning

    Examples:
        .geom_point(position=position_jitter())
        .geom_point(position=position_jitter(width=0.2, height=0))
    """
    params = {}
    if width is not None:
        params["width"] = width
    if height is not None:
        params["height"] = height
    if seed is not None:
        params["seed"] = seed

    return Position("jitter", **params)


def position_jitterdodge(
    jitter_width: Optional[float] = None,
    jitter_height: float = 0.0,
    dodge_width: float = 0.75,
    seed: Optional[int] = None,
) -> Position:
    """
    Adjust position by simultaneous dodging and jittering.

    This is primarily used for aligning points generated through geom_point()
    with dodged boxplots or bar charts.

    Args:
        jitter_width: Degree of jitter in x direction
        jitter_height: Degree of jitter in y direction (default: 0)
        dodge_width: The amount to dodge in the x direction
        seed: Random seed for reproducible results

    Returns:
        Position object for jitterdodge positioning
    """
    params = {"jitter_height": float(jitter_height), "dodge_width": float(dodge_width)}
    if jitter_width is not None:
        params["jitter_width"] = jitter_width
    if seed is not None:
        params["seed"] = seed

    return Position("jitterdodge", **params)


def position_nudge(x: float = 0, y: float = 0) -> Position:
    """
    Adjust position by nudging a given offset.

    Nudging is useful for adjusting the position of elements that would
    otherwise overlap.

    Args:
        x: Horizontal adjustment
        y: Vertical adjustment

    Returns:
        Position object for nudge positioning

    Examples:
        .geom_text(position=position_nudge(y=0.05))
    """
    params = {}
    if x != 0:
        params["x"] = x
    if y != 0:
        params["y"] = y

    return Position("nudge", **params)


def position_stack(vjust: float = 1, reverse: bool = False) -> Position:
    """
    Adjust position by stacking overlapping objects on top of each other.

    position_stack() stacks bars on top of each other; position_fill()
    stacks bars and standardises each stack to have constant height.

    Args:
        vjust: Vertical adjustment for top of stacks
        reverse: If True, will reverse the default stacking order

    Returns:
        Position object for stack positioning
    """
    params = {}
    if vjust != 1:
        params["vjust"] = vjust
    if reverse:
        params["reverse"] = reverse

    return Position("stack", **params)


def position_fill(vjust: float = 1, reverse: bool = False) -> Position:
    """
    Adjust position by stacking and standardizing to constant height.

    position_fill() stacks bars and standardises each stack to have
    constant height. This is useful for showing proportions.

    Args:
        vjust: Vertical adjustment for top of stacks
        reverse: If True, will reverse the default stacking order

    Returns:
        Position object for fill positioning
    """
    params = {}
    if vjust != 1:
        params["vjust"] = vjust
    if reverse:
        params["reverse"] = reverse

    return Position("fill", **params)
