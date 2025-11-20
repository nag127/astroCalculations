# nakshatra_utils.py
# Compute Nakshatra & Pada from sidereal Moon longitude

from config import NAKSHATRAS

NAK_SIZE = 360 / 27   # 13°20' per nakshatra = 13.333333°

def get_nakshatra(moon_sidereal_deg):
    """
    Input: moon sidereal longitude 0..360
    Output: dict with nakshatra name, index, pada, percentages
    """

    # Which nakshatra (0..26)
    nak_index = int(moon_sidereal_deg // NAK_SIZE)

    # Portion completed in this nakshatra
    portion_completed = (moon_sidereal_deg % NAK_SIZE) / NAK_SIZE
    portion_remaining = 1 - portion_completed

    # Pada (1 – 4)
    pada = int(portion_completed * 4) + 1
    if pada > 4:
        pada = 4

    result = {
        "moon_sidereal": moon_sidereal_deg,
        "index": nak_index,
        "nakshatra": NAKSHATRAS[nak_index],
        "pada": pada,
        "portion_completed_percent": round(portion_completed * 100, 4),
        "portion_remaining_percent": round(portion_remaining * 100, 4)
    }

    return result
