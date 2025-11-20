# yogas.py
# Detect common Vedic yogas based on planet placements (inputs: planet_details mapping from astrology_full.py)

from config import SIGNS

def is_gajakesari(planet_details):
    """
    Gajakesari: Moon and Jupiter in kendra (1,4,7,10) from each other;
    classic rule: Moon & Jupiter in kendra (one must be in kendra relative to the other).
    Here we test: Jupiter in a kendra from Moon OR vice versa.
    """
    moon = planet_details.get("Moon")
    jup = planet_details.get("Jupiter")
    if not moon or not jup: return False

    diff = int((jup["longitude"] - moon["longitude"]) // 30) % 12
    # difference in houses (1..12) using degrees -> house difference
    house_diff = (int((jup["longitude"] // 30) - (moon["longitude"] // 30))) % 12
    # kendra are 1,4,7,10 => diffs 0,3,6,9 (0 means same house)
    house_steps = (abs((int(jup["longitude"]//30) - int(moon["longitude"]//30))) ) % 12
    return house_steps in (0,3,6,9)

def is_neechabhanga(planet_details):
    """
    Simplified: check if a debilitated planet has cancellation by lord or exaltation in trikona etc.
    This routine detects simple cases:
    - Planet in debilitation but its dispositor (ruling planet of that sign) is exalted or in kendra from lagna.
    For simplicity, we'll only report candidate debilitated planets.
    """
    results = []
    for name, pd in planet_details.items():
        # simplified check using config: if offset close to debilitation degree (from strengths.EXALTATION)
        # We'll import strengths table if needed; but for brevity, check generic debilitation by sign.
        pass

    return {"note": "Neechabhanga detection requires more detailed rules; returned as placeholder"}

def detect_pancha_mahapurush(planet_details):
    """
    Detects Pancha Mahapurush Yogas: Mars (Ruchaka), Mercury (Bhadra), Jupiter (Hamsa),
    Venus (Malavya), Saturn (Shasha) when they are in their own sign, exaltation? and in kendra.
    We'll implement common pattern:
    planet in its own sign (or exaltation) and in kendra = forms corresponding Mahapurush yoga.
    """
    mahapurush = []
    for p in ("Mars","Mercury","Jupiter","Venus","Saturn"):
        pd = planet_details.get(p)
        if not pd: continue
        sign_idx = pd["sign_index"]
        # Own sign mapping (simplified): exact own-sign checks require sign lord mapping
        # We'll use simple check: if planet is in same sign as its rulership (mapping below)
        lord_of_sign = {
            "Mars": ["Aries","Scorpio"],
            "Mercury": ["Gemini","Virgo"],
            "Jupiter": ["Sagittarius","Pisces"],
            "Venus": ["Taurus","Libra"],
            "Saturn": ["Capricorn","Aquarius"]
        }
        current_sign = pd["sign"]
        if current_sign in lord_of_sign[p]:
            # check if house is kendra
            if pd["house"] in (1,4,7,10):
                mahapurush.append({"type": p+"-Mahapurush", "planet": p, "house": pd["house"], "sign": current_sign})
    return mahapurush

def kemadruma(planet_details):
    """
    Detect Kemadruma Yoga.
    Moon should have:
    - No planets in 2nd or 12th house from Moon's house
    - No conjunction planets with Moon
    """

    moon = planet_details.get("Moon")
    if not moon:
        return {"kemadruma": False, "reason": "Moon not found"}

    moon_house = moon["house"]

    # Houses 2 and 12 from Moon
    house_2 = (moon_house % 12) + 1              # next house
    house_12 = (moon_house - 2) % 12 + 1          # previous house

    # Check for planets in those houses
    planets_in_2_or_12 = []
    planets_conj_moon = []

    for name, pd in planet_details.items():
        if name == "Moon":
            continue

        # Check if planet is in house 2 or 12
        if pd["house"] == house_2 or pd["house"] == house_12:
            planets_in_2_or_12.append(name)

        # Check conjunction within 8° (common rule)
        diff = abs((pd["longitude"] - moon["longitude"] + 180) % 360 - 180)
        if diff < 8:
            planets_conj_moon.append(name)

    # Decision
    if planets_in_2_or_12 or planets_conj_moon:
        return {
            "kemadruma": False,
            "reason": "Moon not isolated",
            "planets_in_2_or_12": planets_in_2_or_12,
            "conjunct_planets": planets_conj_moon
        }

    return {
        "kemadruma": True,
        "reason": "Moon has no planets in 2nd or 12th and no conjunctions",
        "planets_in_2_or_12": [],
        "conjunct_planets": []
    }

def detect_yogas(planet_details):
    found = []
    
    # Gajakesari
    if is_gajakesari(planet_details):
        found.append("Gajakesari Yoga")
    
    # Pancha Mahapurush
    mahapurush_list = detect_pancha_mahapurush(planet_details)
    found.extend([y["type"] for y in mahapurush_list])

    # Kemadruma
    k = kemadruma(planet_details)
    if k["kemadruma"]:
        found.append("Kemadruma Yoga")

    return {
        "yogas": found,
        "diagnostics": {
            "kemadruma": k,
            "mahapurush_details": mahapurush_list
        }
    }
