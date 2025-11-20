import json
import os
from pathlib import Path

import requests

URL = "https://astrocalculations.onrender.com/astrology"
OUTPUT_DIR = Path("api_output_sections")
FULL_OUTPUT_FILE = Path("api_output_sections") / "astrology_output.json"

payload = {
    "dob": "1977-08-04",
    "tob": "01:30",
    "tz": "Asia/Kolkata",
    "latitude": 16.1817369,
    "longitude": 81.1348181,
}

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_section_files(data: dict, directory: Path):
    ensure_dir(directory)
    for key, value in data.items():
        filename = directory / f"{key}.json"
        with filename.open("w", encoding="utf-8") as f:
            json.dump(value, f, indent=2, default=str)


try:
    response = requests.post(URL, json=payload, timeout=60)
    print("STATUS:", response.status_code)
    response.raise_for_status()
    data = response.json()
    ensure_dir(OUTPUT_DIR)
    with FULL_OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    write_section_files(data, OUTPUT_DIR)
    print(f"Saved full response to {FULL_OUTPUT_FILE}")
    print(f"Saved {len(data)} section files in {OUTPUT_DIR}")
except requests.HTTPError:
    print("RAW RESPONSE:")
    print(response.text)
except Exception as exc:
    print(f"Request failed: {exc}")
