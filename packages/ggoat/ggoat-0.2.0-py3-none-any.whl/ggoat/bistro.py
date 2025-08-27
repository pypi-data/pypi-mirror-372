"""
Bistro module: lets-plot statistical and diagnostic plots for ggoat
Implements: image_matrix, corr_plot, qq_plot, joint_plot, residual_plot, waterfall_plot
"""

from typing import Any, Dict

# These functions return lets-plot bistro layer dicts, ready for bridge conversion


def image_matrix(data, *, color_by=None, **kwargs) -> Dict[str, Any]:
    """Create an image matrix plot (heatmap-like)."""
    return {
        "kind": "image_matrix",
        "data": data,
        "color_by": color_by,
        **kwargs,
    }


def corr_plot(data, *, method="pearson", **kwargs) -> Dict[str, Any]:
    """Create a correlation plot."""
    return {"kind": "corr_plot", "data": data, "method": method, **kwargs}


def qq_plot(data, *, distribution="norm", **kwargs) -> Dict[str, Any]:
    """Create a QQ plot."""
    return {
        "kind": "qq_plot",
        "data": data,
        "distribution": distribution,
        **kwargs,
    }


def joint_plot(data, *, x=None, y=None, kind="scatter", **kwargs) -> Dict[str, Any]:
    """Create a joint plot (scatter, hex, density, etc)."""
    return {
        "kind": "joint_plot",
        "data": data,
        "x": x,
        "y": y,
        "joint_kind": kind,
        **kwargs,
    }


def residual_plot(data, *, model=None, **kwargs) -> Dict[str, Any]:
    """Create a residual plot for model diagnostics."""
    return {"kind": "residual_plot", "data": data, "model": model, **kwargs}


def waterfall_plot(data, *, x=None, y=None, **kwargs) -> Dict[str, Any]:
    """Create a waterfall plot."""
    return {"kind": "waterfall_plot", "data": data, "x": x, "y": y, **kwargs}
