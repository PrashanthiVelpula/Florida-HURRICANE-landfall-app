from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TrackPoint:
    dt: datetime
    lat: float
    lon: float
    wind_kt: int
    status: str


@dataclass(frozen=True)
class Storm:
    storm_id: str
    name: str
    points: tuple[TrackPoint, ...]


def _parse_lat_lon(token: str) -> float:
    token = token.strip()
    if not token:
        raise ValueError("empty lat/lon token")

    hemi = token[-1].upper()
    value = float(token[:-1])
    if hemi in ("S", "W"):
        return -value
    if hemi in ("N", "E"):
        return value
    raise ValueError(f"unexpected hemisphere suffix: {token!r}")


def _parse_dt(date_token: str, time_token: str) -> datetime:
    date_token = date_token.strip()
    time_token = time_token.strip().zfill(4)
    # HURDAT2 times are in UTC (best-track convention).
    return datetime.strptime(date_token + time_token, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)


def read_hurdat2(path: str | Path) -> list[Storm]:
    """
    Parse a HURDAT2 text file into storms and track points.

    Important: This parser does NOT use the record identifier (e.g. 'L') for any logic.
    """
    p = Path(path)
    storms: list[Storm] = []

    with p.open("r", encoding="utf-8", errors="replace") as f:
        lines = iter(f)
        for header_line in lines:
            header_line = header_line.strip()
            if not header_line:
                continue

            header = [x.strip() for x in header_line.split(",")]
            if len(header) < 3:
                raise ValueError(f"bad header line: {header_line!r}")

            storm_id = header[0]
            name = header[1] or "UNNAMED"
            try:
                n_entries = int(header[2])
            except ValueError as e:
                raise ValueError(f"bad entry count in header: {header_line!r}") from e

            pts: list[TrackPoint] = []
            for _ in range(n_entries):
                entry_line = next(lines).rstrip("\n")
                cols = [c.strip() for c in entry_line.split(",")]
                if len(cols) < 8:
                    raise ValueError(f"bad entry line: {entry_line!r}")

                dt = _parse_dt(cols[0], cols[1])
                status = cols[3]
                lat = _parse_lat_lon(cols[4])
                lon = _parse_lat_lon(cols[5])
                wind = int(cols[6])
                pts.append(TrackPoint(dt=dt, lat=lat, lon=lon, wind_kt=wind, status=status))

            storms.append(Storm(storm_id=storm_id, name=name, points=tuple(pts)))

    return storms


def iter_points(storms: Iterable[Storm]) -> Iterable[TrackPoint]:
    for s in storms:
        yield from s.points

