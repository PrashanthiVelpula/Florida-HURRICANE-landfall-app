# Florida Hurricane Landfalls (HURDAT2)

This Streamlit app parses NOAA HURDAT2 best-track data and identifies Florida hurricane landfall events since 1900 without using the HURDAT2 landfall (`L`) indicator.

## Problem

The goal is to identify hurricanes that made landfall in Florida since 1900 and output a report containing:

- Storm name
- Date/time of landfall
- Maximum sustained wind speed at landfall

## Approach

Landfall is treated as a geospatial crossing problem:

1. Parse HURDAT2 storm track data into storm objects and track points.
2. Load a Florida land polygon from GeoJSON.
3. For each storm, compare consecutive track points as a line segment.
4. Detect segments that move from outside Florida to inside Florida.
5. Find where that segment intersects Florida's boundary.
6. Interpolate landfall time and wind speed at the boundary crossing.
7. Keep events from 1900 onward with wind speed at landfall greater than or equal to 64 kt.

This makes landfall detection independent of the HURDAT2 `L` field.

## Run Locally

```bash
git clone https://github.com/PrashanthiVelpula/Florida-HURRICANE-landfall-app.git
cd Florida-HURRICANE-landfall-app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then in the Streamlit sidebar:

1. Click **Download HURDAT2 Atlantic**
2. Click **Run analysis**
3. View the landfall table
4. Optionally download the CSV output

## Project Structure

```text
app.py                         Streamlit UI
scripts/download_hurdat2.py    Optional NOAA HURDAT2 downloader
src/hurdat_app/hurdat2.py      HURDAT2 parser
src/hurdat_app/geo.py          Florida GeoJSON loader
src/hurdat_app/landfall.py     Landfall detection logic
src/hurdat_app/report.py       DataFrame/report formatting
```

## Data Sources

- HURDAT2 Atlantic best-track data is downloaded from NOAA.
- Florida boundary data is downloaded as GeoJSON and cached locally as `data/florida_v2.geojson`.
- The full HURDAT2 text file does not need to be committed because the app can download it on first run.

## Implementation Details

### HURDAT2 Parsing

`src/hurdat_app/hurdat2.py` reads the HURDAT2 text file. Each storm has a header line containing storm ID, name, and number of entries, followed by that many track rows.

The parser converts:

- Date/time fields into UTC datetimes
- Latitude/longitude strings like `25.0N` and `80.1W` into signed floats
- Maximum sustained wind into knots

The parser reads the record identifier column, but it does not use the `L` value for any landfall logic.

### Florida Geometry

`src/hurdat_app/geo.py` loads a Florida polygon from GeoJSON. If the file is missing, it downloads and caches it locally. The geometry is converted into a Shapely object so the app can test whether storm points are inside Florida and where storm tracks cross the Florida boundary.

### Landfall Detection

`src/hurdat_app/landfall.py` contains the core algorithm. For each storm:

- Precompute whether each track point is inside Florida.
- Look for outside-to-inside transitions.
- Build a line segment between the two track points.
- Intersect that segment with Florida's boundary.
- Estimate landfall time and wind speed at the intersection point.
- Save events that meet the year and wind-speed filters.

The app uses wind speed at landfall greater than or equal to 64 kt as the hurricane threshold.

### Reporting

`src/hurdat_app/report.py` converts landfall events into a pandas DataFrame. Streamlit displays this table and provides a CSV download.

## Assumptions and Limitations

- Landfall means a storm track crosses from outside Florida land to inside Florida land.
- Hurricane strength is defined as wind speed at landfall greater than or equal to 64 kt.
- Landfall time and wind speed are estimated using linear interpolation between HURDAT2 track points.
- A storm can produce multiple events if it leaves and re-enters Florida.
- Results depend on the resolution of the HURDAT2 data and the Florida GeoJSON boundary.
- Shapely treats latitude/longitude coordinates as planar coordinates here. 

