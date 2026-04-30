from __future__ import annotations

from pathlib import Path

import requests

HURDAT2_ATLANTIC_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt"


def main() -> int:
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / Path(HURDAT2_ATLANTIC_URL).name
    print(f"Downloading: {HURDAT2_ATLANTIC_URL}")
    resp = requests.get(HURDAT2_ATLANTIC_URL, timeout=180)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    print(f"Saved to: {out_path}")
    print(f"Bytes: {out_path.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

