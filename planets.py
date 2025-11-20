# planets.py
from astronomy import get_planet_longitude
from ayanamsa import calculate_ayanamsa

PLANETS = {
    "Sun": "Sun",
    "Moon": "Moon",
    "Mars": "Mars",
    "Mercury": "Mercury",
    "Jupiter": "Jupiter Barycenter",
    "Venus": "Venus",
    "Saturn": "Saturn Barycenter"
}

RAHU_KETU_OFFSET = 180

def get_sidereal_planets(dt, lat, lon, tz_str):
    ayan = calculate_ayanamsa(dt)
    positions = {}

    for planet_name, eph_name in PLANETS.items():
        lon_tropical = get_planet_longitude(dt, lat, lon, tz_str, eph_name)
        sidereal = (lon_tropical - ayan) % 360
        positions[planet_name] = sidereal

    # Rahu and Ketu (mean nodes)
    rahu = (positions["Moon"] + 180) % 360
    ketu = (rahu + 180) % 360

    positions["Rahu"] = rahu
    positions["Ketu"] = ketu

    return positions
