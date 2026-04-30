from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from .landfall import LandfallEvent


def events_to_dataframe(events: list[LandfallEvent]) -> pd.DataFrame:
    df = pd.DataFrame([asdict(e) for e in events])
    if df.empty:
        return df
    df["landfall_dt"] = pd.to_datetime(df["landfall_dt"], utc=True)
    df = df.sort_values(["landfall_dt", "name", "storm_id"]).reset_index(drop=True)
    return df


def format_report_lines(events: list[LandfallEvent]) -> list[str]:
    # Minimal plain-text report.
    lines = ["name, landfall_utc, wind_kt, lat, lon, storm_id"]
    for e in events:
        lines.append(
            f"{e.name}, {e.landfall_dt.strftime('%Y-%m-%d %H:%M')}, {e.wind_kt}, {e.lat:.3f}, {e.lon:.3f}, {e.storm_id}"
        )
    return lines

