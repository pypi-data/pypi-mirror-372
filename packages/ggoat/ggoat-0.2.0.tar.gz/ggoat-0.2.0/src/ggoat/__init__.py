"""
ggoat: Grammar of Graphics for Python - optimized for Pyodide and browser environments

A clean, lightweight implementation of ggplot2's Grammar of Graphics for Python,
designed specifically for modern web environments including Pyodide, Jupyter,
and browser-based Python.

Key Features:
    * Method chaining for readable plot construction
    * Minimal dependencies (works with Python stdlib)
    * Browser-optimized rendering via lets-plot
    * Support for both dict and pandas DataFrame data
    * Comprehensive Grammar of Graphics implementation

Simple API - import only what you need:
    * ggplot: Main plotting class with method chaining
    * aes: Aesthetic mappings for data variables to visual properties

Example:
    >>> from ggoat import ggplot, aes
    >>> data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
    >>> plot = ggplot(data, aes(x='x', y='y')).geom_point().theme_minimal()
    >>> plot.show()

Documentation: https://ggoat.readthedocs.io/
Repository: https://github.com/ggoat/ggoat
"""

__version__ = "0.2.4"

from .aes import aes
from .bistro import (corr_plot, image_matrix, joint_plot, qq_plot,
                     residual_plot, waterfall_plot)
from .core import ggplot
from .geospatial import (TILE_CARTODB, TILE_GOOGLE, TILE_OSM,
                         TILE_STAMEN_TERRAIN, TILE_STAMEN_TONER,
                         TILE_STAMEN_WATERCOLOR, geocode, maptiles)
from .positions import (position_dodge, position_dodge2, position_fill,
                        position_identity, position_jitter,
                        position_jitterdodge, position_nudge, position_stack)
from .scales import (guide_colorbar, guide_legend, guides, layer_key, lims,
                     scale_alpha, scale_alpha_identity, scale_alpha_manual,
                     scale_brewer, scale_cmapmpl, scale_color_brewer,
                     scale_color_cmapmpl, scale_color_discrete,
                     scale_color_gradient, scale_color_gradient2,
                     scale_color_gradientn, scale_color_grey, scale_color_hue,
                     scale_color_identity, scale_color_manual,
                     scale_color_viridis, scale_continuous, scale_discrete,
                     scale_fill_brewer, scale_fill_cmapmpl,
                     scale_fill_discrete, scale_fill_gradient,
                     scale_fill_gradient2, scale_fill_gradientn,
                     scale_fill_grey, scale_fill_hue, scale_fill_identity,
                     scale_fill_manual, scale_fill_viridis, scale_gradient,
                     scale_gradient2, scale_gradientn, scale_grey, scale_hue,
                     scale_identity, scale_linetype_identity,
                     scale_linetype_manual, scale_linewidth,
                     scale_linewidth_identity, scale_manual, scale_shape,
                     scale_shape_identity, scale_shape_manual, scale_size,
                     scale_size_area, scale_size_identity, scale_size_manual,
                     scale_stroke, scale_stroke_identity, scale_viridis,
                     scale_x_continuous, scale_x_datetime, scale_x_discrete,
                     scale_x_discrete_reversed, scale_x_log2, scale_x_log10,
                     scale_x_reverse, scale_x_time, scale_y_continuous,
                     scale_y_datetime, scale_y_discrete,
                     scale_y_discrete_reversed, scale_y_log2, scale_y_log10,
                     scale_y_reverse, scale_y_time, xlim, ylim)
from .themes import (element_blank, element_line, element_rect, element_text,
                     theme, theme_bw, theme_classic, theme_grey, theme_light,
                     theme_minimal, theme_void)


def setup_notebook():
    from lets_plot import LetsPlot

    LetsPlot.setup_html()


# Optionally export new method names for direct import (for user discoverability)
flavor_darcula = ggplot.flavor_darcula
flavor_high_contrast_dark = ggplot.flavor_high_contrast_dark
flavor_high_contrast_light = ggplot.flavor_high_contrast_light
flavor_solarized_dark = ggplot.flavor_solarized_dark
flavor_solarized_light = ggplot.flavor_solarized_light
sampling_random = ggplot.sampling_random
sampling_random_stratified = ggplot.sampling_random_stratified
sampling_pick = ggplot.sampling_pick
sampling_systematic = ggplot.sampling_systematic
sampling_group_random = ggplot.sampling_group_random
sampling_group_systematic = ggplot.sampling_group_systematic
sampling_vertex_vw = ggplot.sampling_vertex_vw
sampling_vertex_dp = ggplot.sampling_vertex_dp
layer_tooltips = ggplot.layer_tooltips
font_metrics_adjustment = ggplot.font_metrics_adjustment
font_family_info = ggplot.font_family_info

__all__ = [
    "ggplot",
    "aes",
    "setup_notebook",
    # Bistro
    "image_matrix",
    "corr_plot",
    "qq_plot",
    "joint_plot",
    "residual_plot",
    "waterfall_plot",
    # Geospatial
    "geocode",
    "maptiles",
    "TILE_OSM",
    "TILE_CARTODB",
    "TILE_GOOGLE",
    "TILE_STAMEN_TONER",
    "TILE_STAMEN_TERRAIN",
    "TILE_STAMEN_WATERCOLOR",
    # Scales
    "scale_color_manual",
    "scale_fill_manual",
    "scale_color_gradient",
    "scale_fill_gradient",
    "scale_x_discrete",
    "scale_y_discrete",
    "scale_x_discrete_reversed",
    "scale_y_discrete_reversed",
    "scale_x_continuous",
    "scale_y_continuous",
    "scale_x_log10",
    "scale_y_log10",
    "scale_x_log2",
    "scale_y_log2",
    "scale_x_reverse",
    "scale_y_reverse",
    "scale_color_gradient2",
    "scale_fill_gradient2",
    "scale_color_gradientn",
    "scale_fill_gradientn",
    "scale_color_hue",
    "scale_fill_hue",
    "scale_color_discrete",
    "scale_fill_discrete",
    "scale_color_grey",
    "scale_fill_grey",
    "scale_color_brewer",
    "scale_fill_brewer",
    "scale_color_viridis",
    "scale_fill_viridis",
    "scale_color_cmapmpl",
    "scale_fill_cmapmpl",
    "scale_manual",
    "scale_continuous",
    "scale_discrete",
    "scale_gradient",
    "scale_gradient2",
    "scale_gradientn",
    "scale_hue",
    "scale_grey",
    "scale_brewer",
    "scale_viridis",
    "scale_cmapmpl",
    "scale_shape",
    "scale_shape_manual",
    "scale_size_manual",
    "scale_size",
    "scale_size_area",
    "scale_linewidth",
    "scale_stroke",
    "scale_alpha_manual",
    "scale_alpha",
    "scale_linetype_manual",
    "scale_x_datetime",
    "scale_y_datetime",
    "scale_x_time",
    "scale_y_time",
    "scale_identity",
    "scale_color_identity",
    "scale_fill_identity",
    "scale_shape_identity",
    "scale_linetype_identity",
    "scale_alpha_identity",
    "scale_size_identity",
    "scale_linewidth_identity",
    "scale_stroke_identity",
    "lims",
    "xlim",
    "ylim",
    "guide_legend",
    "guide_colorbar",
    "guides",
    "layer_key",
    # Themes
    "theme_minimal",
    "theme_bw",
    "theme_classic",
    "theme_grey",
    "theme_light",
    "theme_void",
    "theme",
    "element_text",
    "element_line",
    "element_rect",
    "element_blank",
    # Positions
    "position_dodge",
    "position_dodge2",
    "position_jitter",
    "position_jitterdodge",
    "position_nudge",
    "position_stack",
    "position_fill",
    "position_identity",
    # Flavors
    "flavor_darcula",
    "flavor_high_contrast_dark",
    "flavor_high_contrast_light",
    "flavor_solarized_dark",
    "flavor_solarized_light",
    # Sampling
    "sampling_random",
    "sampling_random_stratified",
    "sampling_pick",
    "sampling_systematic",
    "sampling_group_random",
    "sampling_group_systematic",
    "sampling_vertex_vw",
    "sampling_vertex_dp",
    # Tooltips & font features
    "layer_tooltips",
    "font_metrics_adjustment",
    "font_family_info",
]
