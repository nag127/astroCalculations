from astrology_full import astrology_full
import json
from pathlib import Path


def save_output(payload, filename="astrology_output.json"):
    path = Path(filename)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return str(path.resolve())


if __name__ == "__main__":
    result = astrology_full(
        dob="1977-08-04",
        tob="01:30",
        tz_str="Asia/Kolkata",
        latitude=16.1817369,
        longitude=81.1348181
    )

    filepath = save_output(result)
    print(f"Astrology data saved to {filepath}")