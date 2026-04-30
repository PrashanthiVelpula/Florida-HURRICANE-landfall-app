from __future__ import annotations

import json
from pathlib import Path

import requests
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union


DEFAULT_CACHE_DIR = Path("data")
# Cache filename is versioned to avoid stale/low-res polygons.
DEFAULT_FLORIDA_GEOJSON = DEFAULT_CACHE_DIR / "florida_v2.geojson"

# Public-domain US-states GeoJSON (Florida feature only).
FLORIDA_GEOJSON_URL = "https://raw.githubusercontent.com/glynnbird/usstatesgeojson/master/florida.geojson"


def _ensure_cache_dir(cache_dir: Path) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)


def load_florida_geometry(
    florida_geojson_path: str | Path = DEFAULT_FLORIDA_GEOJSON,
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
) -> BaseGeometry:
    """
    Returns a shapely geometry representing Florida land area.

    Behavior:
    - If `florida_geojson_path` exists, loads it.
    - Otherwise downloads a US-states GeoJSON (Natural Earth derived), extracts Florida, caches it, and loads.
    """
    florida_geojson_path = Path(florida_geojson_path)
    cache_dir = Path(cache_dir)
    _ensure_cache_dir(cache_dir)

    if not florida_geojson_path.exists():
        resp = requests.get(FLORIDA_GEOJSON_URL, timeout=60)
        resp.raise_for_status()
        florida_geojson_path.write_text(resp.text, encoding="utf-8")

    data = json.loads(florida_geojson_path.read_text(encoding="utf-8"))

    # Accept either a FeatureCollection or a single Feature.
    geoms = []
    if data.get("type") == "Feature":
        geom = data.get("geometry")
        if geom:
            geoms.append(shape(geom))
    else:
        for ft in data.get("features", []):
            geom = ft.get("geometry")
            if geom:
                geoms.append(shape(geom))

    if not geoms:
        raise ValueError(f"No geometries found in {florida_geojson_path}")

    return unary_union(geoms)

