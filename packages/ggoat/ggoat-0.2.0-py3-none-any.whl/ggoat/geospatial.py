"""
Geospatial utilities and constants for lets-plot/ggoat
Implements: geocode, maptiles, tile constants
"""

from typing import Any, Dict


# Geocode utility (stub, for API compatibility)
def geocode(address: str, provider: str = "osm", **kwargs) -> Dict[str, Any]:
    """Return a geocode query dict for lets-plot."""
    return {
        "kind": "geocode",
        "address": address,
        "provider": provider,
        **kwargs,
    }


# Maptiles utility (returns a maptiles layer dict)
def maptiles(kind: str = "osm", **kwargs) -> Dict[str, Any]:
    """Return a maptiles layer dict for lets-plot."""
    return {"kind": "maptiles", "provider": kind, **kwargs}


# Tile provider constants (for user convenience)
TILE_OSM = "osm"
TILE_CARTODB = "carto"
TILE_GOOGLE = "google"
TILE_STAMEN_TONER = "stamen_toner"
TILE_STAMEN_TERRAIN = "stamen_terrain"
TILE_STAMEN_WATERCOLOR = "stamen_watercolor"
