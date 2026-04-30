from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry

from .hurdat2 import Storm


@dataclass(frozen=True)
class LandfallEvent:
    storm_id: str
    name: str
    landfall_dt: datetime
    wind_kt: int
    lat: float
    lon: float


def _pick_intersection_point(line: LineString, intersection) -> Point | None:
    """
    Return a single Point on the segment boundary intersection.

    Intersections can be:
    - empty
    - Point
    - MultiPoint
    - (rarely) LineString if segment overlaps boundary; we ignore those.
    """
    if intersection.is_empty:
        return None

    geom_type = intersection.geom_type
    if geom_type == "Point":
        return intersection
    if geom_type == "MultiPoint":
        # Choose the first intersection along the segment.
        pts = list(intersection.geoms)
        pts.sort(key=lambda p: line.project(p))
        return pts[0] if pts else None

    return None


def _lerp_dt(t0: datetime, t1: datetime, frac: float) -> datetime:
    dt = t1 - t0
    return t0 + timedelta(seconds=dt.total_seconds() * frac)


def find_florida_landfalls(
    storms: list[Storm],
    florida_geom: BaseGeometry,
    *,
    since_year: int = 1900,
    hurricane_wind_threshold_kt: int = 64,
) -> list[LandfallEvent]:
    """
    Identify Florida landfall events by geometry crossing (water -> land).

    We intentionally do not use HURDAT2's record identifier 'L' landfall flag.
    """
    events: list[LandfallEvent] = []

    for storm in storms:
        pts = storm.points
        if len(pts) < 2:
            continue

        inside = [florida_geom.contains(Point(p.lon, p.lat)) for p in pts]

        for i in range(1, len(pts)):
            if inside[i - 1] or not inside[i]:
                continue

            p0 = pts[i - 1]
            p1 = pts[i]

            line = LineString([(p0.lon, p0.lat), (p1.lon, p1.lat)])
            ip = _pick_intersection_point(line, line.intersection(florida_geom.boundary))
            if ip is None:
                # Fallback: use first point inside (coarser but avoids dropping events).
                ip = Point(p1.lon, p1.lat)
                frac = 1.0
            else:
                seg_len = line.length
                frac = 1.0 if seg_len == 0 else float(line.project(ip) / seg_len)

            landfall_dt = _lerp_dt(p0.dt, p1.dt, frac)
            wind = int(round(p0.wind_kt + frac * (p1.wind_kt - p0.wind_kt)))

            if landfall_dt.year < since_year:
                continue
            if wind < hurricane_wind_threshold_kt:
                continue

            events.append(
                LandfallEvent(
                    storm_id=storm.storm_id,
                    name=storm.name,
                    landfall_dt=landfall_dt,
                    wind_kt=wind,
                    lat=float(ip.y),
                    lon=float(ip.x),
                )
            )

    events.sort(key=lambda e: (e.landfall_dt, e.name, e.storm_id))
    return events

