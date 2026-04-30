# Florida Hurricane Landfalls (HURDAT2)

Small app that parses NOAA HURDAT2 best-track data and identifies **Florida landfall events since 1900** **without using** the HURDAT2 landfall (`L`) indicator.

## How landfall is detected (no `L`)

- Load a **Florida land polygon** (GeoJSON).
- For each storm track segment, detect **outside → inside** transitions.
- Compute the **boundary intersection** of the segment with Florida’s polygon and linearly interpolate:
  - landfall timestamp
  - maximum sustained wind (kt)
- Keep events with interpolated wind \(\ge 64\) kt (hurricane threshold) and year \(\ge 1900\).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Get HURDAT2

Download the HURDAT2 Atlantic dataset from NOAA (HURDAT2 format spec + data are under `https://www.nhc.noaa.gov/data/`).

Put the file somewhere locally, e.g. `data/hurdat2-atlantic.txt`.

Or download it with the included script:

```bash
python scripts/download_hurdat2.py
```

## Run the UI

```bash
streamlit run app.py
```

## Notes

- On first run, the app will download a US-states GeoJSON from a public-domain Natural Earth derived dataset and cache a Florida-only GeoJSON under `data/florida.geojson` (you can also provide your own).
- On first run, the app will download a public-domain Florida GeoJSON and cache it under `data/florida_v2.geojson` (you can also provide your own).
- This project intentionally does **not** use the HURDAT2 record identifier `L` as a landfall signal.

