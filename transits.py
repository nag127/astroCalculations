# transits.py
# compute gochar/transit comparisons and Sade-Sati detection

from astronomy import get_planet_longitudes
from datetime import datetime
from ayanamsa import calculate_ayanamsa

def current_transits(dt, latitude, longitude, tz_str, sidereal=True):
    """Return current planetary longitudes (sidereal if sidereal=True)."""
    return get_planet_longitudes(dt, latitude, longitude, tz_str, sidereal=sidereal)

def transit_vs_natal(natal_planets, transit_planets):
    """
    Compare transit longitudes to natal longitudes and return differences
    (useful for transit aspects, conjunctions).
    natal_planets & transit_planets are dicts {name: lon}
    """
    diffs = {}
    for name, natal_lon in natal_planets.items():
        t_lon = transit_planets.get(name)
        if t_lon is None: continue
        diff = abs((t_lon - natal_lon + 180) % 360 - 180)
        diffs[name] = {"natal": natal_lon, "transit": t_lon, "angular_diff": diff}
    return diffs

def sade_sati(natal_moon_lon, saturn_transit_lon):
    """
    Sade-Sati occurs when Saturn transits the 12th, 1st, and 2nd house from natal Moon.
    Simplified detection:
    - Houses: 12th = -30..0 from moon, 1st = 0..30, 2nd = 30..60 (in degrees)
    We'll compute Saturn's position relative to natal Moon.
    """
    diff = (saturn_transit_lon - natal_moon_lon + 360) % 360
    if 330 <= diff <= 360 or 0 <= diff < 30:
        phase = "1st (over natal moon) or 12th depending on boundary"
    elif 30 <= diff < 60:
        phase = "2nd"
    elif 300 <= diff < 330:
        phase = "12th"
    else:
        phase = "not in Sade-Sati zone"
    # More nuanced detection requires Saturn's long-term transit (entry dates).
    return {"diff_deg": diff, "phase": phase}

def rahu_ketu_transit(transit_planets):
    """Return Rahu/Ketu positions if available in transit_planets map."""
    return {"Rahu": transit_planets.get("Rahu"), "Ketu": transit_planets.get("Ketu")}
