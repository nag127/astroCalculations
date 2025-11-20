# strengths.py
# Evaluate planetary strengths (basic) for Vedic interpretation.

from datetime import datetime
from ayanamsa import calculate_ayanamsa

# Basic tables
EXALTATION = {
    "Sun": 10,    # 10° Aries
    "Moon": 3,    # 3° Taurus
    "Mars": 28,   # 28° Capricorn
    "Mercury": 15,# 15° Virgo
    "Jupiter": 5, # 5° Cancer
    "Venus": 27,  # 27° Pisces
    "Saturn": 20  # 20° Libra
}
DEBILITATION = {k: (v + 180) % 30 for k, v in EXALTATION.items()}  # simple opposite

def in_sign(degree):
    """Return sign index and offset (0..11, 0..30)."""
    idx = int(degree // 30)
    offset = degree % 30
    return idx, offset

def is_exalted(planet_long):
    idx, offset = in_sign(planet_long)
    # compare offset to exaltation table (by sign's offset)
    name_offsets = {k: v for k, v in EXALTATION.items()}
    # we need planet name to check; caller should pass (name, long)
    raise NotImplementedError("Use planet_strength(name, longitude)")

def planet_strength(name, longitude, date=None, retrograde=False, sun_longitude=None):
    """
    Return a small strength summary dict for given planet.
    name: 'Sun','Moon',...
    longitude: sidereal longitude (deg)
    retrograde: bool (if known)
    sun_longitude: sidereal Sun lon for combustion check
    """
    idx, offset = in_sign(longitude)
    # Exaltation/debilitation check:
    ex_deg = EXALTATION.get(name)
    if ex_deg is not None:
        ex_status = abs((offset - ex_deg + 15) % 30 - 15) < 1.0  # within 1° considered exalted
        deb_status = abs((offset - DEBILITATION[name] + 15) % 30 - 15) < 1.0
    else:
        ex_status = False
        deb_status = False

    # Combustion (classic rules vary). We'll use approximate:
    combustion = False
    if sun_longitude is not None and name != "Sun":
        diff = abs((longitude - sun_longitude + 180) % 360 - 180)
        # classic combustion thresholds (approx): Mercury ~ 14', Venus ~ 10', others different.
        threshold = 11  # degrees approx for demonstration (you may refine)
        combustion = diff < threshold

    strength_score = 0
    # simple scoring
    if ex_status:
        strength_score += 3
    if deb_status:
        strength_score -= 3
    if retrograde:
        strength_score += 1
    if combustion:
        strength_score -= 2

    return {
        "planet": name,
        "longitude": round(longitude, 6),
        "sign_index": idx,
        "offset_in_sign": offset,
        "is_exalted": ex_status,
        "is_debilitated": deb_status,
        "is_retrograde": retrograde,
        "is_combust": combustion,
        "raw_score": strength_score
    }
