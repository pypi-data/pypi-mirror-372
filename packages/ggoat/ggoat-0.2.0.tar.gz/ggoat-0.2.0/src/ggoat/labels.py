"""
Labels and annotations for ggplot.

This module provides functions for adding titles, axis labels, and other
text elements to plots.
"""

from typing import Optional


class labs:
    """
    Add labels to a plot.

    labs() allows you to set the title, subtitle, caption, and axis labels
    for your plot.
    """

    def __init__(
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
        Create labels for plot elements.

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
        """
        self.labels = {}
        self.component_type = "labels"

        # Main plot labels
        if title is not None:
            self.labels["title"] = title
        if subtitle is not None:
            self.labels["subtitle"] = subtitle
        if caption is not None:
            self.labels["caption"] = caption

        # Axis labels
        if x is not None:
            self.labels["x"] = x
        if y is not None:
            self.labels["y"] = y

        # Aesthetic labels - handle color/colour compatibility
        color_label = color if color is not None else colour
        if color_label is not None:
            self.labels["color"] = color_label

        if fill is not None:
            self.labels["fill"] = fill
        if size is not None:
            self.labels["size"] = size
        if shape is not None:
            self.labels["shape"] = shape
        if alpha is not None:
            self.labels["alpha"] = alpha
        if linetype is not None:
            self.labels["linetype"] = linetype

        # Additional labels from kwargs
        for key, value in kwargs.items():
            if value is not None:
                self.labels[key] = value

    def add_to_plot(self, plot):
        """Add labels to a plot."""
        plot.labels.update(self.labels)

    def __repr__(self) -> str:
        """String representation of labels."""
        label_strs = [f"{k}='{v}'" for k, v in self.labels.items()]
        return f"labs({', '.join(label_strs)})"


# Convenience functions
def xlab(label: str) -> labs:
    """Set x-axis label."""
    return labs(x=label)


def ylab(label: str) -> labs:
    """Set y-axis label."""
    return labs(y=label)


def ggtitle(label: str, subtitle: Optional[str] = None) -> labs:
    """Set plot title and optional subtitle."""
    return labs(title=label, subtitle=subtitle)
