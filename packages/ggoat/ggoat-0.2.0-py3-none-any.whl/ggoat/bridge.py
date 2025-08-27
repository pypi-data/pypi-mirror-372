"""
Bridge module for communicating with lets-plot JavaScript library.
This module handles:
- Loading the lets-plot JavaScript library
- Converting Python plot specifications to lets-plot format
- Managing JavaScript interop for Pyodide environments
- Rendering plots in the browser
"""

import json
import uuid
from pathlib import Path
from typing import Any, Dict


class LetsPlotBridge:
    """
    Bridge between Python ggplot API and lets-plot JavaScript library.

    This class handles the communication protocol between Python and the
    lets-plot JavaScript library, including plot specification conversion
    and rendering management.
    """

    def __init__(self):
        """Initialize the bridge."""
        self._js_loaded = False
        self._plot_counter = 0

    def ensure_js_loaded(self) -> bool:
        """
        Ensure the lets-plot JavaScript library is loaded.

        Returns:
            True if successfully loaded, False otherwise
        """
        if self._js_loaded:
            return True

        try:
            # Try to detect environment
            if self._is_pyodide():
                return self._load_js_pyodide()
            elif self._is_jupyter():
                return self._load_js_jupyter()
            else:
                # Standalone Python - limited functionality
                return self._load_js_standalone()
        except Exception as e:
            print(f"Failed to load lets-plot JavaScript: {e}")
            return False

    def _is_pyodide(self) -> bool:
        """Check if running in Pyodide environment."""
        try:
            import sys

            return "pyodide" in sys.modules
        except Exception:
            return False

    def _is_jupyter(self) -> bool:
        """Check if running in Jupyter environment."""
        try:
            from IPython import get_ipython

            return get_ipython() is not None
        except ImportError:
            return False

    def _load_js_pyodide(self) -> bool:
        """Load JavaScript library in Pyodide environment."""
        try:
            # In Pyodide, we can use js module to interact with JavaScript
            from js import console
            from js import eval as js_eval

            # Load the lets-plot JavaScript file
            js_path = self._get_js_path()
            with open(js_path, "r") as f:
                js_code = f.read()

            # Execute the JavaScript code
            js_eval(js_code)

            # Check if LetsPlot is available
            if hasattr(__import__("js"), "LetsPlot"):
                console.log(
                    "✅ ggoat: lets-plot JavaScript library loaded successfully"
                )
                self._js_loaded = True
                return True
            else:
                console.log("❌ ggoat: LetsPlot object not found after loading")
                return False

        except Exception as e:
            print(f"Failed to load JavaScript in Pyodide: {e}")
            return False

    def _load_js_jupyter(self) -> bool:
        """Load JavaScript library in Jupyter environment."""
        try:
            # Prefer to use the official lets_plot Python package when available
            # — it will have already initialized the JS runtime for the frontend.
            import importlib.util

            if importlib.util.find_spec("lets_plot") is not None:
                self._js_loaded = True
                return True
            else:
                # Fallback: inject bundled lets-plot JS into the notebook frontend
                from IPython.display import HTML, Javascript, display

                # Load the lets-plot JavaScript file
                js_path = self._get_js_path()
                with open(js_path, "r") as f:
                    js_code = f.read()

                # Inject JS into the notebook. Using display(Javascript(...)) does
                # not return a value to the python caller, so it won't produce a
                # stray <IPython.core.display.Javascript object> in the output.
                display(Javascript(js_code))
                display(
                    HTML(
                        """
                <script>
                (function() {
                    if (typeof LetsPlot !== 'undefined') {
                        console.log(
                            '✅ ggoat: lets-plot JavaScript library loaded in Jupyter'
                        );
                    } else {
                        console.log('❌ ggoat: LetsPlot object not found after loading');
                    }
                })();
                </script>
                """
                    )
                )

                self._js_loaded = True
                return True

        except Exception as e:
            print(f"Failed to load JavaScript in Jupyter: {e}")
            return False

    def _load_js_standalone(self) -> bool:
        """Handle standalone Python environment (limited functionality)."""
        print("⚠️  ggoat: Running in standalone Python environment.")
        print("   Plot rendering requires Pyodide or Jupyter environment.")
        print("   You can still build plot specifications and export to JSON.")
        self._js_loaded = False
        return False

    def _get_js_path(self) -> Path:
        """Get path to the bundled lets-plot JavaScript file."""
        return Path(__file__).parent / "assets" / "lets-plot.min.js"

    def render_plot(self, plot_spec: Dict[str, Any]) -> str:
        """
        Render a plot from its specification.

        Args:
            plot_spec: Complete plot specification dictionary

        Returns:
            HTML string containing the rendered plot
        """
        if not self.ensure_js_loaded():
            return self._render_fallback(plot_spec)

        try:
            if self._is_pyodide():
                return self._render_pyodide(plot_spec)
            elif self._is_jupyter():
                return self._render_jupyter(plot_spec)
            else:
                return self._render_fallback(plot_spec)
        except Exception as e:
            print(f"Failed to render plot: {e}")
            return self._render_fallback(plot_spec)

    def _render_pyodide(self, plot_spec: Dict[str, Any]) -> str:
        """Render plot in Pyodide environment."""
        from js import console

        # Generate unique plot ID
        plot_id = f"ggoat_plot_{self._plot_counter}"
        self._plot_counter += 1

        try:
            # Convert plot spec to lets-plot format
            lets_plot_spec = self._convert_to_lets_plot_spec(plot_spec)

            # Create container div
            container_html = (
                f'<div id="{plot_id}" style="width: 100%; height: 400px;"></div>'
            )

            # Use lets-plot to render
            plot_json = json.dumps(lets_plot_spec)

            # Call LetsPlot JavaScript API
            js_code = f"""
            try {{
                const spec = {plot_json};
                const plotDiv = document.getElementById('{plot_id}');
                if (plotDiv && typeof LetsPlot !== 'undefined') {{
                    LetsPlot.buildPlotFromProcessedSpecs(spec, -1, -1, plotDiv);
                    console.log('✅ Plot rendered successfully');
                }} else {{
                    console.error('❌ Plot container or LetsPlot not found');
                }}
            }} catch (e) {{
                console.error('❌ Error rendering plot:', e);
            }}
            """

            # Execute JavaScript
            from js import eval as js_eval

            js_eval(js_code)

            return container_html

        except Exception as e:
            console.error(f"❌ Pyodide rendering error: {e}")
            return self._render_fallback(plot_spec)

    def _render_jupyter(self, plot_spec: Dict[str, Any]) -> str:
        """Render plot in Jupyter environment."""

        try:
            import importlib.util

            # First, try to use lets_plot package directly if available
            if importlib.util.find_spec("lets_plot") is not None:
                ggoat_spec = self._convert_to_lets_plot_native(plot_spec)
                return ggoat_spec

            # Generate unique plot ID
            plot_id = f"ggoat_plot_{self._plot_counter}"
            self._plot_counter += 1

            # Convert plot spec to lets-plot format
            lets_plot_spec = self._convert_to_lets_plot_spec(plot_spec)
            plot_json = json.dumps(lets_plot_spec)

            # Create HTML container
            html_content = (
                f'<div id="{plot_id}"\n'
                '     style="width: 100%; height: 400px; border: 1px solid #ccc;">\n'
                '</div>\n'
                '<script>\n'
                'try {\n'
                f'    const spec = {plot_json};\n'
                f'    const plotDiv = document.getElementById("{plot_id}");\n'
                '    if (plotDiv && typeof LetsPlot !== "undefined") {\n'
                '        LetsPlot.buildPlotFromProcessedSpecs('
                'spec, -1, -1, plotDiv);\n'
                "        console.log('✅ Plot rendered successfully in Jupyter');\n"
                '    } else {\n'
                "        console.error('❌ Plot container or LetsPlot missing');\n"
                '        plotDiv.innerHTML = \'<p">Error: LetsPlot not '
                'loaded</p>\';\n'
                '    }\n'
                '} catch (e) {\n'
                "    console.error('❌ Error rendering plot in Jupyter:', e);\n"
                f'    document.getElementById("{plot_id}").innerHTML = (\n'
                "        '<p style=\"color: red;\">Error rendering plot: ' + "
                '        e.message + \'</p>\'\n'
                '    );\n'
                '}\n'
                '</script>\n'
            )

            return html_content

        except Exception as e:
            print(f"Jupyter rendering error: {e}")
            return self._render_fallback(plot_spec)

            # Generate unique plot ID
            plot_id = f"ggoat_plot_{self._plot_counter}"
            self._plot_counter += 1

            # Convert plot spec to lets-plot format
            lets_plot_spec = self._convert_to_lets_plot_spec(plot_spec)
            plot_json = json.dumps(lets_plot_spec)

            # Create HTML container
            html_content = (
                f'<div id="{plot_id}" style="width: 100%; height: 400px;\n'
                '    border: 1px solid #ccc;"></div>\n'
                '<script>\n'
                'try {\n'
                f'    const spec = {plot_json};\n'
                f'    const plotDiv = document.getElementById("{plot_id}");\n'
                '    if (plotDiv && typeof LetsPlot !== "undefined") {\n'
                '        LetsPlot.buildPlotFromProcessedSpecs('
                '            spec, -1, -1, plotDiv);\n'
                "        console.log('✅ Plot rendered successfully in Jupyter');\n"
                '    } else {\n'
                "        console.error('❌ Plot container or LetsPlot missing');\n"
                '        plotDiv.innerHTML = \'<p>Error: LetsPlot not '
                '            loaded</p>\';\n'
                '    }\n'
                '} catch (e) {\n'
                "    console.error('❌ Error rendering plot in Jupyter:', e);\n"
                f'    document.getElementById("{plot_id}").innerHTML = (\n'
                "        '<p style=\"color: red;\">Error rendering plot: ' + "
                '        e.message + \'</p>\'\n'
                '    );\n'
                '}\n'
                '</script>\n'
            )

            return html_content

        except Exception as e:
            print(f"Jupyter rendering error: {e}")
            return self._render_fallback(plot_spec)

    def _convert_to_lets_plot_native(self, plot_spec: Dict[str, Any]):
        """Convert ggoat spec to native lets_plot object."""
        import importlib

        lp = importlib.import_module("lets_plot")

        # Start with data and determine effective facet
        data = plot_spec.get("data", {})
        effective_facet = plot_spec.get("facet") or plot_spec.get("facets")

        # Grid facets are handled at facet-application time below. We prefer
        # calling native lp.facet_grid (so separate row/col strips are used).
        # If facet_grid fails, we will create a composite column and use
        # facet_wrap as a robust fallback.

        # Prepare aesthetic mapping
        mapping_dict = plot_spec.get("mapping", {})
        mapping = lp.aes(**mapping_dict) if mapping_dict else None

        # Create base plot
        plot = lp.ggplot(data, mapping)

        # Add layers
        for layer in plot_spec.get("layers", []):
            geom_type = layer.get("geom", "point")
            params = layer.get("params", {}) or {}
            layer_mapping_dict = layer.get("mapping", {}) or {}

            # Create layer mapping
            layer_mapping = lp.aes(**layer_mapping_dict) if layer_mapping_dict else None

            # Add appropriate geom
            try:
                if geom_type == "point":
                    geom = lp.geom_point(mapping=layer_mapping, **params)
                elif geom_type == "line":
                    geom = lp.geom_line(mapping=layer_mapping, **params)
                elif geom_type == "bar":
                    geom = lp.geom_bar(mapping=layer_mapping, **params)
                elif geom_type == "histogram":
                    geom = lp.geom_histogram(mapping=layer_mapping, **params)
                elif geom_type == "smooth":
                    geom = lp.geom_smooth(mapping=layer_mapping, **params)
                elif geom_type == "boxplot":
                    geom = lp.geom_boxplot(mapping=layer_mapping, **params)
                elif geom_type == "violin":
                    geom = lp.geom_violin(mapping=layer_mapping, **params)
                elif geom_type == "text":
                    geom = lp.geom_text(mapping=layer_mapping, **params)
                elif geom_type == "jitter":
                    geom = lp.geom_jitter(mapping=layer_mapping, **params)
                elif geom_type == "density":
                    geom = lp.geom_density(mapping=layer_mapping, **params)
                elif geom_type == "area":
                    geom = lp.geom_area(mapping=layer_mapping, **params)
                else:
                    # Unknown geom: skip
                    continue

                plot = plot + geom
            except Exception:
                # Don't let a single layer break the whole plot
                continue

        # Add facets if present
        if effective_facet:
            try:
                if (
                    isinstance(effective_facet, dict)
                    and "rows" in effective_facet
                    and "cols" in effective_facet
                ):
                    plot = plot + lp.facet_grid(**effective_facet)
                else:
                    plot = plot + lp.facet_wrap(effective_facet)
            except Exception:
                pass

        # Add labels if present
        labels = plot_spec.get("labels", {}) or {}
        if labels:
            plot = plot + lp.labs(**labels)

        # Add coordinate system if present
        coord = plot_spec.get("coord")
        if coord:
            try:
                plot = plot + getattr(lp, f"coord_{coord}")()
            except Exception:
                pass

        # Add scales if present
        scales = plot_spec.get("scales", [])
        for scale in scales:
            try:
                scale_type = scale.get("type")
                if scale_type:
                    plot = plot + getattr(lp, scale_type)(**scale.get("params", {}))
            except Exception:
                pass

        # Add theme if present
        theme = plot_spec.get("theme")
        if theme:
            try:
                plot = plot + getattr(lp, f"theme_{theme}")()
            except Exception:
                pass

        return plot

        # Start with data and determine effective facet
        data = plot_spec.get("data", {})
        effective_facet = plot_spec.get("facet") or plot_spec.get("facets")

        # Grid facets are handled at facet-application time below. We prefer
        # calling native lp.facet_grid (so separate row/col strips are used).
        # If facet_grid fails, we will create a composite column and use
        # facet_wrap as a robust fallback.

        # Prepare aesthetic mapping
        mapping_dict = plot_spec.get("mapping", {})
        mapping = lp.aes(**mapping_dict) if mapping_dict else None

        # Create base plot
        plot = lp.ggplot(data, mapping)

        # Add layers
        for layer in plot_spec.get("layers", []):
            geom_type = layer.get("geom", "point")
            params = layer.get("params", {}) or {}
            layer_mapping_dict = layer.get("mapping", {}) or {}

            # Create layer mapping
            layer_mapping = lp.aes(**layer_mapping_dict) if layer_mapping_dict else None

            # Add appropriate geom
            try:
                if geom_type == "point":
                    geom = lp.geom_point(mapping=layer_mapping, **params)
                elif geom_type == "line":
                    geom = lp.geom_line(mapping=layer_mapping, **params)
                elif geom_type == "bar":
                    geom = lp.geom_bar(mapping=layer_mapping, **params)
                elif geom_type == "histogram":
                    geom = lp.geom_histogram(mapping=layer_mapping, **params)
                elif geom_type == "smooth":
                    geom = lp.geom_smooth(mapping=layer_mapping, **params)
                elif geom_type == "boxplot":
                    geom = lp.geom_boxplot(mapping=layer_mapping, **params)
                elif geom_type == "violin":
                    geom = lp.geom_violin(mapping=layer_mapping, **params)
                elif geom_type == "text":
                    geom = lp.geom_text(mapping=layer_mapping, **params)
                elif geom_type == "jitter":
                    geom = lp.geom_jitter(mapping=layer_mapping, **params)
                elif geom_type == "density":
                    geom = lp.geom_density(mapping=layer_mapping, **params)
                elif geom_type == "area":
                    geom = lp.geom_area(mapping=layer_mapping, **params)
                else:
                    # Unknown geom: skip
                    continue

                plot = plot + geom
            except Exception:
                # Don't let a single layer break the whole plot
                continue

        # Add labels
        labels = plot_spec.get("labels", {}) or {}
        if labels.get("title"):
            try:
                plot = plot + lp.ggtitle(labels["title"], labels.get("subtitle"))
            except Exception:
                pass
        if labels.get("x"):
            try:
                plot = plot + lp.xlab(labels["x"])
            except Exception:
                pass
        if labels.get("y"):
            try:
                plot = plot + lp.ylab(labels["y"])
            except Exception:
                pass

        # Apply facet settings if present
        facet = effective_facet
        if facet:
            try:
                ftype = facet.get("type", "wrap")
                if ftype == "wrap":
                    vars_raw = facet.get("vars", [])
                    vars_list = (
                        vars_raw if isinstance(vars_raw, (list, tuple)) else [vars_raw]
                    )
                    if hasattr(lp, "facet_wrap"):
                        try:
                            if len(vars_list) == 1:
                                plot = plot + lp.facet_wrap(
                                    vars_list[0],
                                    nrow=facet.get("nrow"),
                                    ncol=facet.get("ncol"),
                                    scales=facet.get("scales"),
                                )
                            else:
                                plot = plot + lp.facet_wrap(
                                    vars_list,
                                    nrow=facet.get("nrow"),
                                    ncol=facet.get("ncol"),
                                    scales=facet.get("scales"),
                                )
                        except TypeError:
                            # Fallback: try positional args
                            plot = plot + lp.facet_wrap(*vars_list)
                elif ftype == "grid":
                    rows = facet.get("rows")
                    cols = facet.get("cols")
                    # Only use native facet_grid with correct API (x=cols, y=rows)
                    if hasattr(lp, "facet_grid"):
                        try:
                            # Unwrap single-item lists to strings
                            def _unwrap(val):
                                if isinstance(val, (list, tuple)) and len(val) == 1:
                                    return val[0]
                                elif isinstance(val, (list, tuple)) and len(val) > 1:
                                    return val[0]  # Take first item if multiple
                                return val

                            row_var = _unwrap(rows) if rows else None
                            col_var = _unwrap(cols) if cols else None

                            plot = plot + lp.facet_grid(
                                x=col_var,
                                y=row_var,
                                scales=facet.get("scales"),
                            )
                        except Exception:
                            # If facet_grid fails, skip faceting
                            pass
            except Exception:
                # Don't break rendering if facet application fails
                pass

        # Apply coordinate settings if present
        coord = plot_spec.get("coord")
        if coord:
            try:
                ctype = coord.get("type")
                if ctype == "cartesian" and hasattr(lp, "coord_cartesian"):
                    try:
                        plot = plot + lp.coord_cartesian(
                            xlim=coord.get("xlim"),
                            ylim=coord.get("ylim"),
                            expand=coord.get("expand", True),
                        )
                    except TypeError:
                        plot = plot + lp.coord_cartesian(
                            coord.get("xlim"), coord.get("ylim")
                        )
                elif ctype == "flip" and hasattr(lp, "coord_flip"):
                    try:
                        plot = plot + lp.coord_flip(
                            xlim=coord.get("xlim"),
                            ylim=coord.get("ylim"),
                            expand=coord.get("expand", True),
                        )
                    except TypeError:
                        plot = plot + lp.coord_flip(
                            coord.get("xlim"), coord.get("ylim")
                        )
                elif ctype == "fixed" and hasattr(lp, "coord_fixed"):
                    try:
                        plot = plot + lp.coord_fixed(
                            ratio=coord.get("ratio", 1),
                            xlim=coord.get("xlim"),
                            ylim=coord.get("ylim"),
                            expand=coord.get("expand", True),
                        )
                    except Exception:
                        pass
                elif ctype == "polar" and hasattr(lp, "coord_polar"):
                    try:
                        plot = plot + lp.coord_polar(
                            theta=coord.get("theta", "x"),
                            start=coord.get("start", 0),
                            direction=coord.get("direction", 1),
                        )
                    except Exception:
                        pass
                elif ctype == "map" and hasattr(lp, "coord_map"):
                    try:
                        plot = plot + lp.coord_map(
                            projection=coord.get("projection", "mercator"),
                            xlim=coord.get("xlim"),
                            ylim=coord.get("ylim"),
                            expand=coord.get("expand", True),
                        )
                    except Exception:
                        pass
            except Exception:
                pass

        # Apply scales if present
        scales = plot_spec.get("scales", [])
        for scale in scales:
            try:
                aesthetic = scale.get("aesthetic")
                scale_type = scale.get("type")

                if aesthetic == "color":
                    if scale_type == "manual":
                        values = scale.get("values")
                        if values:
                            plot = plot + lp.scale_color_manual(
                                values=values,
                                name=scale.get("name"),
                                breaks=scale.get("breaks"),
                                labels=scale.get("labels"),
                                limits=scale.get("limits"),
                                guide=scale.get("guide"),
                            )
                    elif scale_type == "gradient":
                        plot = plot + lp.scale_color_gradient(
                            low=scale.get("low", "#132B43"),
                            high=scale.get("high", "#56B1F7"),
                            name=scale.get("name"),
                            breaks=scale.get("breaks"),
                            labels=scale.get("labels"),
                            limits=scale.get("limits"),
                            guide=scale.get("guide"),
                        )

                elif aesthetic == "fill":
                    if scale_type == "manual":
                        values = scale.get("values")
                        if values:
                            plot = plot + lp.scale_fill_manual(
                                values=values,
                                name=scale.get("name"),
                                breaks=scale.get("breaks"),
                                labels=scale.get("labels"),
                                limits=scale.get("limits"),
                                guide=scale.get("guide"),
                            )
                    elif scale_type == "gradient":
                        plot = plot + lp.scale_fill_gradient(
                            low=scale.get("low", "#132B43"),
                            high=scale.get("high", "#56B1F7"),
                            name=scale.get("name"),
                            breaks=scale.get("breaks"),
                            labels=scale.get("labels"),
                            limits=scale.get("limits"),
                            guide=scale.get("guide"),
                        )
            except Exception as e:
                # Don't break rendering if scale application fails
                print(f"Warning: Failed to apply {aesthetic} scale: {e}")
                pass

        # Apply theme/flavor if present
        theme = plot_spec.get("theme")
        if theme:
            try:
                # Flavors as special theme dicts
                if isinstance(theme, dict) and "flavor" in theme:
                    flavor = theme["flavor"]
                    if flavor == "darcula" and hasattr(lp, "flavor_darcula"):
                        plot = plot + lp.flavor_darcula()
                    elif flavor == "high_contrast_dark" and hasattr(
                        lp, "flavor_high_contrast_dark"
                    ):
                        plot = plot + lp.flavor_high_contrast_dark()
                    elif flavor == "high_contrast_light" and hasattr(
                        lp, "flavor_high_contrast_light"
                    ):
                        plot = plot + lp.flavor_high_contrast_light()
                    elif flavor == "solarized_dark" and hasattr(
                        lp, "flavor_solarized_dark"
                    ):
                        plot = plot + lp.flavor_solarized_dark()
                    elif flavor == "solarized_light" and hasattr(
                        lp, "flavor_solarized_light"
                    ):
                        plot = plot + lp.flavor_solarized_light()
                elif hasattr(theme, "theme_type"):
                    if theme.theme_type == "predefined":
                        theme_name = getattr(theme, "theme_name", None)
                        if theme_name == "minimal" and hasattr(lp, "theme_minimal"):
                            plot = plot + lp.theme_minimal()
                        elif theme_name == "bw" and hasattr(lp, "theme_bw"):
                            plot = plot + lp.theme_bw()
                        elif theme_name == "classic" and hasattr(lp, "theme_classic"):
                            plot = plot + lp.theme_classic()
                        elif theme_name == "grey" and hasattr(lp, "theme_grey"):
                            plot = plot + lp.theme_grey()
                        elif theme_name == "light" and hasattr(lp, "theme_light"):
                            plot = plot + lp.theme_light()
                        elif theme_name == "void" and hasattr(lp, "theme_void"):
                            plot = plot + lp.theme_void()
                    elif theme.theme_type == "custom":
                        properties = getattr(theme, "properties", {})
                        if properties and hasattr(lp, "theme"):
                            plot = plot + lp.theme(**properties)
            except Exception as e:
                print(f"Warning: Failed to apply theme/flavor: {e}")
                pass
        # Tooltips, font features, sampling:
        # (pass as metainfo for lets-plot JS or as layer params if supported)
        # Not all are natively supported in lets-plot Python API,
        # but can be passed in JS spec
        # Add to metainfo_list if present
        for meta_key in [
            "tooltips",
            "font_metrics",
            "font_family_info",
            "sampling",
        ]:
            meta_val = (
                getattr(plot_spec, meta_key, None)
                if hasattr(plot_spec, meta_key)
                else plot_spec.get(meta_key)
            )
            if meta_val:
                try:
                    if hasattr(plot, "add_meta"):  # lets-plot >=4.0
                        plot = plot.add_meta(meta_key, meta_val)
                    else:
                        # Add to metainfo_list for JS
                        if hasattr(plot, "metainfo_list"):
                            plot.metainfo_list.append(
                                {"name": meta_key, "value": meta_val}
                            )
                except Exception:
                    pass

        return plot

    def _render_fallback(self, plot_spec: Dict[str, Any]) -> str:
        """Fallback rendering for unsupported environments."""
        plot_id = f"ggoat_plot_{self._plot_counter}"
        self._plot_counter += 1

        # Convert to lets-plot spec to make it JSON serializable
        try:
            lets_plot_spec = self._convert_to_lets_plot_spec(plot_spec)
            spec_json = json.dumps(lets_plot_spec, indent=2)
        except Exception as e:
            # Fallback to basic representation if conversion fails
            spec_json = f"Error converting plot spec: {e}"

        # Return a basic HTML representation
        return (
            f'<div id="{plot_id}" '
            'style="padding: 20px; border: 2px dashed #ccc;\n'
            '    text-align: center;">\n'
            '    <h3>🐐 ggoat Plot</h3>\n'
            '    <p><strong>Environment:</strong> Standalone Python '
            '(limited functionality)</p>\n'
            '    <p>For full plot rendering, use in Pyodide.</p>\n'
            '    <details>\n'
            '        <summary>Plot Specification (JSON)</summary>\n'
            '        <pre style="text-align: left; background: #f5f5f5;\n'
            '            padding: 10px; overflow: auto;">\n'
            f'{spec_json}\n'
            '        </pre>\n'
            '    </details>\n'
            '</div>\n'
        )

    def _convert_to_lets_plot_spec(self, plot_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert ggoat plot specification to lets-plot format.

        Args:
            plot_spec: ggoat plot specification

        Returns:
            lets-plot compatible specification
        """
        # Build lets-plot spec in the format it expects
        lets_plot_spec = {
            "kind": "plot",
            "data": plot_spec.get("data", {}),
            "mapping": self._convert_mapping(plot_spec.get("mapping", {})),
            "layers": [],
            "scales": [],
            # Provide JS-friendly metadata containers
            "data_meta": plot_spec.get("data_meta", {}),
            "metainfo_list": [],
            "spec_id": str(uuid.uuid4()),
        }

        # Add labels if present
        labels = plot_spec.get("labels", {})
        if labels:
            lets_plot_spec["ggtitle"] = {
                "text": labels.get("title", ""),
                "subtitle": labels.get("subtitle", ""),
            }
            if labels.get("x"):
                lets_plot_spec["xlab"] = labels["x"]
            if labels.get("y"):
                lets_plot_spec["ylab"] = labels["y"]

        # Add facet information if present in ggoat spec
        facet = plot_spec.get("facet")
        if facet:
            # Pass through facet structure — duplicate under both keys to
            # satisfy different internal consumers in lets-plot JS.
            # Normalize facet representation for 'grid' type: the JS expects
            # an array of facet descriptors for rows/cols rather than plain
            # string lists. Transform if necessary.
            normalized = (
                dict(facet)
                if isinstance(facet, dict)
                else {"type": "wrap", "vars": facet}
            )

            if normalized.get("type") == "grid":
                # rows/cols may be lists of names (['a']) or single name
                def to_descriptors(vals):
                    if vals is None:
                        return None
                    if isinstance(vals, (str,)):
                        return [{"name": vals}]
                    if isinstance(vals, (list, tuple)):
                        return [{"name": v} if isinstance(v, str) else v for v in vals]
                    return vals

                normalized_rows = to_descriptors(normalized.get("rows"))
                normalized_cols = to_descriptors(normalized.get("cols"))
                normalized["rows"] = normalized_rows
                normalized["cols"] = normalized_cols

                # Some consumers look for nrow/ncol at top level
                if normalized.get("nrow") is not None:
                    lets_plot_spec["nrow"] = normalized.get("nrow")
                if normalized.get("ncol") is not None:
                    lets_plot_spec["ncol"] = normalized.get("ncol")

            lets_plot_spec["facet"] = normalized
            # some parts of the JS expect a 'facets' key name
            lets_plot_spec["facets"] = normalized
            # also add to metainfo_list so any metainfo-driven code can find it
            try:
                lets_plot_spec["metainfo_list"].append(
                    {"name": "facets", "value": normalized}
                )
            except Exception:
                pass

        # Add coordinate information if present
        coord = plot_spec.get("coord")
        if coord:
            lets_plot_spec["coord"] = coord
            # Keep coord also in metainfo_list for completeness
            try:
                lets_plot_spec["metainfo_list"].append(
                    {"name": "coord", "value": coord}
                )
            except Exception:
                pass

        # Convert layers to lets-plot format
        for layer in plot_spec.get("layers", []):
            # Support Bistro/geospatial utilities (kind-based)
            kind = layer.get("kind")
            if kind in {
                "image_matrix",
                "corr_plot",
                "qq_plot",
                "joint_plot",
                "residual_plot",
                "waterfall_plot",
            }:
                # Pass through as a bistro layer
                lets_plot_layer = dict(layer)
                lets_plot_layer["kind"] = kind
                lets_plot_spec["layers"].append(lets_plot_layer)
                continue
            if kind in {"geocode", "maptiles"}:
                # Pass through as a geospatial layer
                lets_plot_layer = dict(layer)
                lets_plot_layer["kind"] = kind
                lets_plot_spec["layers"].append(lets_plot_layer)
                continue

            # Default: treat as a regular geom layer
            lets_plot_layer = {
                "kind": "layer",
                "geom": self._map_geom_name(layer.get("geom", "point")),
                "stat": layer.get("stat", "identity"),
                "position": self._convert_position(layer.get("position", "identity")),
                "mapping": self._convert_mapping(layer.get("mapping", {})),
            }
            # Add layer-specific data if present
            if layer.get("data"):
                lets_plot_layer["data"] = layer["data"]
            # Add geom-specific parameters
            params = layer.get("params", {})
            if params:
                for param_name, param_value in params.items():
                    lets_plot_layer[param_name] = param_value
            lets_plot_spec["layers"].append(lets_plot_layer)
        return lets_plot_spec

    def _convert_mapping(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ggoat aesthetic mapping to lets-plot format."""
        if not mapping:
            return {}

        converted = {}
        for aesthetic, value in mapping.items():
            # In lets-plot, aesthetics map directly to data column names
            if isinstance(value, str):
                # Column reference
                converted[aesthetic] = value
            else:
                # Constant value - needs special handling in lets-plot
                converted[aesthetic] = value

        return converted

    def _map_geom_name(self, geom_name: str) -> str:
        """Map ggoat geom names to lets-plot geom names."""
        # Most geom names are the same, but some might need mapping
        geom_mapping = {
            "point": "point",
            "line": "line",
            "bar": "bar",
            "histogram": "histogram",
            "smooth": "smooth",
            "boxplot": "boxplot",
            "violin": "violin",
            "text": "text",
            "jitter": "jitter",
            "density": "density",
            "area": "area",
            "path": "path",
            "count": "count",
            "tile": "tile",
            "errorbar": "errorbar",
            "lollipop": "lollipop",
            "pie": "pie",
            "dotplot": "dotplot",
            "bin2d": "bin2d",
            "hex": "hex",
            "raster": "raster",
            "crossbar": "crossbar",
            "linerange": "linerange",
            "pointrange": "pointrange",
            "contour": "contour",
            "contourf": "contourf",
            "polygon": "polygon",
            "map": "map",
            "abline": "abline",
            "hline": "hline",
            "vline": "vline",
            "band": "band",
            "ribbon": "ribbon",
            "density2d": "density2d",
            "density2df": "density2df",
            "freqpoly": "freqpoly",
            "step": "step",
            "rect": "rect",
            "segment": "segment",
            "curve": "curve",
            "spoke": "spoke",
            "text_repel": "text_repel",
            "label": "label",
            "label_repel": "label_repel",
            "qq": "qq",
            "qq2": "qq2",
            "qq_line": "qq_line",
            "qq2_line": "qq2_line",
            "function": "function",
            "blank": "blank",
            "imshow": "imshow",
            "livemap": "livemap",
        }
        return geom_mapping.get(geom_name, geom_name)

    def _convert_position(self, position):
        """Convert position object or string to lets-plot format."""
        # Import Position here to avoid circular imports
        try:
            from .positions import Position
        except ImportError:
            # If positions module not available, just return as string
            return str(position) if position else "identity"

        if isinstance(position, Position):
            # Convert Position object to lets-plot format
            pos_dict = {"kind": position.position_type}
            # Add all parameters from the Position object
            if hasattr(position, "params") and position.params:
                pos_dict.update(position.params)
            return pos_dict
        else:
            # Return as string for basic positions
            return str(position) if position else "identity"

    def save_plot(
        self,
        plot_spec: Dict[str, Any],
        filename: str,
        width: int = 600,
        height: int = 400,
        format: str = "html",
    ) -> bool:
        """
        Save plot to file.

        Args:
            plot_spec: Plot specification
            filename: Output filename
            width: Plot width in pixels
            height: Plot height in pixels
            format: Output format ('html', 'json')

        Returns:
            True if successful, False otherwise
        """
        try:
            if format.lower() == "json":
                # Save as JSON specification
                with open(filename, "w") as f:
                    json.dump(plot_spec, f, indent=2)
                return True
            elif format.lower() == "html":
                # Save as HTML file with embedded plot
                html_content = self._create_standalone_html(plot_spec, width, height)
                with open(filename, "w") as f:
                    f.write(html_content)
                return True
            else:
                print(f"Unsupported format: {format}")
                return False
        except Exception as e:
            print(f"Failed to save plot: {e}")
            return False

    def _create_standalone_html(
        self, plot_spec: Dict[str, Any], width: int, height: int
    ) -> str:
        """Create a standalone HTML file with embedded plot."""
        lets_plot_spec = self._convert_to_lets_plot_spec(plot_spec)
        plot_json = json.dumps(lets_plot_spec)

        # Read the lets-plot JavaScript
        js_path = self._get_js_path()
        with open(js_path, "r") as f:
            lets_plot_js = f.read()

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ggoat Plot</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        #plot {{ width: {width}px; height: {height}px; border: 1px solid #ddd; }}
        .header {{ margin-bottom: 20px; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🐐 ggoat Plot</h2>
        <p>Generated by ggoat - ggplot2 Grammar of Graphics for Pyodide</p>
    </div>
    <div id="plot"></div>
    <div class="footer">
    <p>Rendered using
        <a href="https://github.com/JetBrains/lets-plot" target="_blank">
        lets-plot
        </a>
        JavaScript library
    </p>
    </div>

    <script>
{lets_plot_js}
    </script>

    <script>
        try {{
            const spec = {plot_json};
            const plotDiv = document.getElementById('plot');
            if (typeof LetsPlot !== 'undefined') {{
                LetsPlot.buildPlotFromProcessedSpecs(spec, {width}, {height}, plotDiv);
                console.log('✅ Plot rendered successfully');
            }} else {{
                plotDiv.innerHTML = '<p>Error: LetsPlot library not loaded</p>';
                console.error('❌ LetsPlot library not found');
            }}
        }} catch (e) {{
            console.error('❌ Error rendering plot:', e);
            document.getElementById('plot').innerHTML = (
                '<p style="color: red;">Error rendering plot: ' + e.message + '</p>'
            );
        }}
    </script>
</body>
</html>
        """

        return html_template
