from __future__ import annotations

from pathlib import Path

import requests
import streamlit as st

from src.hurdat_app.geo import load_florida_geometry
from src.hurdat_app.hurdat2 import read_hurdat2
from src.hurdat_app.landfall import find_florida_landfalls
from src.hurdat_app.report import events_to_dataframe


st.set_page_config(page_title="Florida Hurricane Landfalls (HURDAT2)", layout="wide")

st.title("Florida hurricane landfalls since 1900 (HURDAT2)")
st.caption("Landfall is detected by track crossing into Florida’s land polygon (no HURDAT2 'L' flag).")

HURDAT2_ATLANTIC_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt"

with st.sidebar:
    st.subheader("Inputs")
    hurdat_path = st.text_input(
        "HURDAT2 file path",
        value=st.session_state.get("hurdat_path", str(Path("data") / Path(HURDAT2_ATLANTIC_URL).name)),
        key="hurdat_path",
    )
    florida_geojson_path = st.text_input("Florida GeoJSON cache/path", value=str(Path("data") / "florida_v2.geojson"))
    since_year = st.number_input("Since year", min_value=1851, max_value=2100, value=1900, step=1)
    min_wind = st.number_input("Min wind at landfall (kt)", min_value=0, max_value=300, value=64, step=1)
    
    st.divider()
    st.subheader("Download (optional)")
    st.caption("Download the Atlantic HURDAT2 text file from NOAA into `data/`.")
    download_target = st.text_input("Download to", value=str(Path("data") / Path(HURDAT2_ATLANTIC_URL).name))
    download = st.button("Download HURDAT2 Atlantic", type="secondary")
    run = st.button("Run analysis", type="primary")

if download:
    target = Path(download_target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with st.status("Downloading HURDAT2…", expanded=False):
        r = requests.get(HURDAT2_ATLANTIC_URL, timeout=180)
        r.raise_for_status()
        target.write_bytes(r.content)
    #st.session_state["hurdat_path"] = str(target)
    st.success(f"Downloaded to: {target}")

if run:
    hurdat_file = Path(hurdat_path)
    if not hurdat_file.exists():
        st.error(f"HURDAT2 file not found: {hurdat_file}")
        st.stop()

    with st.status("Loading Florida geometry…", expanded=False):
        fl = load_florida_geometry(florida_geojson_path)

    with st.status("Parsing HURDAT2…", expanded=False):
        storms = read_hurdat2(hurdat_file)

    with st.status("Detecting landfalls…", expanded=False):
        events = find_florida_landfalls(storms, fl, since_year=int(since_year), hurricane_wind_threshold_kt=int(min_wind))

    df = events_to_dataframe(events)

    c1, c2 = st.columns([1, 1])
    c1.metric("Landfall events", value=len(df))
    c2.metric("Unique storms", value=int(df["storm_id"].nunique()) if not df.empty else 0)

    st.dataframe(df, use_container_width=True, height=520)

    if not df.empty:
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="florida_hurricane_landfalls_since_1900.csv",
            mime="text/csv",
        )

else:
    st.info("Provide a local HURDAT2 file path, then click **Run analysis**.")

