"""
Utility functions for ggoat.

This module provides helper functions for working with the ggoat package,
including JavaScript loading and environment detection.
"""

import sys
from pathlib import Path


def load_js() -> bool:
    """
    Manually load the lets-plot JavaScript library.

    This function can be called explicitly to ensure the JavaScript
    library is loaded before creating plots.

    Returns:
        True if successfully loaded, False otherwise
    """
    from .bridge import LetsPlotBridge

    bridge = LetsPlotBridge()
    return bridge.ensure_js_loaded()


def is_pyodide() -> bool:
    """
    Check if running in a Pyodide environment.

    Returns:
        True if running in Pyodide, False otherwise
    """
    try:
        return "pyodide" in sys.modules
    except Exception:
        return False


def is_jupyter() -> bool:
    """
    Check if running in a Jupyter environment.

    Returns:
        True if running in Jupyter, False otherwise
    """
    try:
        from IPython import get_ipython

        return get_ipython() is not None
    except ImportError:
        return False


def get_environment_info() -> dict:
    """
    Get information about the current environment.

    Returns:
        Dictionary with environment information
    """
    info = {
        "python_version": sys.version,
        "is_pyodide": is_pyodide(),
        "is_jupyter": is_jupyter(),
        "ggoat_version": None,
    }

    # Try to get ggoat version
    try:
        from . import __version__

        info["ggoat_version"] = __version__
    except ImportError:
        info["ggoat_version"] = "unknown"

    return info


def check_dependencies() -> dict:
    """
    Check if required dependencies are available.

    Returns:
        Dictionary with dependency status
    """
    deps = {}

    # Check pandas
    try:
        import pandas

        deps["pandas"] = {"available": True, "version": pandas.__version__}
    except ImportError:
        deps["pandas"] = {"available": False, "version": None}

    # Check numpy
    try:
        import numpy

        deps["numpy"] = {"available": True, "version": numpy.__version__}
    except ImportError:
        deps["numpy"] = {"available": False, "version": None}

    # Check JavaScript environment
    deps["javascript"] = {
        "pyodide_available": is_pyodide(),
        "jupyter_available": is_jupyter(),
    }

    return deps


def get_asset_path(filename: str) -> Path:
    """
    Get the path to a bundled asset file.

    Args:
        filename: Name of the asset file

    Returns:
        Path to the asset file
    """
    return Path(__file__).parent / "assets" / filename


def diagnose() -> None:
    """
    Print diagnostic information about the ggoat installation.

    This function prints information about the environment,
    dependencies, and asset files to help debug issues.
    """
    print("🐐 ggoat Diagnostic Information")
    print("=" * 40)

    # Environment info
    print("\n📍 Environment:")
    env_info = get_environment_info()
    for key, value in env_info.items():
        print(f"  {key}: {value}")

    # Dependencies
    print("\n📦 Dependencies:")
    deps = check_dependencies()
    for dep_name, dep_info in deps.items():
        if isinstance(dep_info, dict) and "available" in dep_info:
            status = "✅" if dep_info["available"] else "❌"
            version = f" (v{dep_info['version']})" if dep_info["version"] else ""
            print(f"  {status} {dep_name}{version}")
        else:
            print(f"  📋 {dep_name}: {dep_info}")

    # Asset files
    print("\n🗂️  Assets:")
    assets_dir = Path(__file__).parent / "assets"
    if assets_dir.exists():
        for asset_file in assets_dir.iterdir():
            size_mb = asset_file.stat().st_size / (1024 * 1024)
            print(f"  ✅ {asset_file.name} ({size_mb:.1f}MB)")
    else:
        print("  ❌ Assets directory not found")

    # Recommendations
    print("\n💡 Recommendations:")
    if not deps["pandas"]["available"]:
        print("  • Install pandas: pip install pandas")
    if not deps["numpy"]["available"]:
        print("  • Install numpy: pip install numpy")
    if not (
        deps["javascript"]["pyodide_available"]
        or deps["javascript"]["jupyter_available"]
    ):
        print("  • For full functionality, use in Pyodide or Jupyter environment")
    if deps["pandas"]["available"] and deps["numpy"]["available"]:
        print("  • All dependencies satisfied! 🎉")

    print("\n" + "=" * 40)
