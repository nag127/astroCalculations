# astronomy.py

from skyfield.api import load, wgs84
import pytz
from datetime import datetime
from ayanamsa import calculate_ayanamsa

# The full DE441 kernel is > 3GB and cannot be memory-mapped by 32-bit Python.
# Use the lighter DE421 kernel instead so the project works on all platforms.
EPHEMERIS_FILE = 'de421.bsp'

try:
    eph = load(EPHEMERIS_FILE)
except Exception as exc:  # pragma: no cover - load happens at import time
    raise RuntimeError(
        f"Failed to load ephemeris '{EPHEMERIS_FILE}'. "
        "Ensure the BSP file is present and readable."
    ) from exc

# Planet positions from the kernel (geocentric when combined with Earth observer)
planets_sf = {
    "Sun": eph["sun"],
    "Moon": eph["moon"],
    "Mercury": eph["mercury"],
    "Venus": eph["venus"],
    "Mars": eph["mars"],
    "Jupiter": eph["jupiter barycenter"],
    "Saturn": eph["saturn barycenter"],
}

# Earth center for building a topocentric observer
earth = eph["earth"]


def skyfield_time(dt, tz_str):
    try:
        tz = pytz.timezone(tz_str)
    except pytz.UnknownTimeZoneError as exc:
        raise ValueError(f"Unknown timezone '{tz_str}'.") from exc

    try:
        dt_local = tz.localize(dt)
    except Exception as exc:
        raise ValueError(f"Could not localize datetime {dt} for timezone {tz_str}.") from exc

    ts = load.timescale()
    return ts.from_datetime(dt_local)


# ----------------------------------------------------
# Convert planet to TOPOCENTRIC longitude
# ----------------------------------------------------
def planet_topocentric_longitude(planet, t, lat, lon):
    try:
        observer = (earth + wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon)).at(t)
        topo = observer.observe(planet).apparent()
        _, lon_deg, _ = topo.ecliptic_latlon()
        return lon_deg.degrees % 360
    except Exception as exc:
        raise RuntimeError(
            f"Failed to compute topocentric longitude for lat={lat}, lon={lon}"
        ) from exc


# ----------------------------------------------------
# Moon longitude
# ----------------------------------------------------
def get_moon_longitude(dt, lat, lon, tz_str):
    t = skyfield_time(dt, tz_str)
    return planet_topocentric_longitude(planets_sf["Moon"], t, lat, lon)


# ----------------------------------------------------
# All planets (tropical)
# ----------------------------------------------------
def get_tropical_planets(dt, lat, lon, tz_str):
    t = skyfield_time(dt, tz_str)

    results = {}
    for name, planet in planets_sf.items():
        results[name] = planet_topocentric_longitude(planet, t, lat, lon)

    return results


# ----------------------------------------------------
# Sidereal planets
# ----------------------------------------------------
def get_sidereal_planets(dt, lat, lon, tz_str):
    tropical = get_tropical_planets(dt, lat, lon, tz_str)
    ayan = calculate_ayanamsa(dt)
    return {name: (deg - ayan) % 360 for name, deg in tropical.items()}


# ----------------------------------------------------
# Lagna (Ascendant)
# ----------------------------------------------------
def calculate_lagna(dt, lat, lon, tz_str):
    t = skyfield_time(dt, tz_str)

    observer = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon).at(t)

    asc = observer.from_altaz(alt_degrees=0, az_degrees=90)
    _, lon_deg, _ = asc.ecliptic_latlon()

    return lon_deg.degrees % 360


def get_planet_longitudes(dt, lat, lon, tz_str, sidereal=True):
    if sidereal:
        return get_sidereal_planets(dt, lat, lon, tz_str)
    else:
        return get_tropical_planets(dt, lat, lon, tz_str)
