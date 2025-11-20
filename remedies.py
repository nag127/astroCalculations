# remedies.py
# Simple rule-based remedial suggestions (high-level).

REMEDY_DB = {
    "Sun": {
        "mantra": "Om Suryaya Namaha",
        "gemstone": "Ruby",
        "color": "Red",
        "donation": "Donate wheat or jaggery to the needy"
    },
    "Moon": {
        "mantra": "Om Chandraya Namaha",
        "gemstone": "Pearl/White Sapphire",
        "color": "White",
        "donation": "Donate milk, white clothes"
    },
    "Mars": {
        "mantra": "Om Mangalaya Namaha",
        "gemstone": "Red Coral",
        "color": "Red",
        "donation": "Donate red lentils"
    },
    "Venus": {
        "mantra": "Om Shukraya Namaha",
        "gemstone": "Diamond/Opal",
        "color": "White/Pastel",
        "donation": "Donate sweets, perfumes"
    },
    "Jupiter": {
        "mantra": "Om Gurave Namaha",
        "gemstone": "Yellow Sapphire",
        "color": "Yellow",
        "donation": "Donate yellow clothes or turmeric"
    },
    "Saturn": {
        "mantra": "Om Shanaischaraya Namaha",
        "gemstone": "Blue Sapphire (use carefully)",
        "color": "Black/Blue",
        "donation": "Donate black clothes, iron"
    },
    "Mercury": {
        "mantra": "Om Budhaya Namaha",
        "gemstone": "Emerald",
        "color": "Green",
        "donation": "Donate green vegetables"
    },
    "Rahu": {
        "mantra": "Om Raam Rahave Namaha",
        "gemstone": "Hessonite (Gomed)",
        "donation": "Donate sesame, blankets"
    },
    "Ketu": {
        "mantra": "Om Ketave Namaha",
        "gemstone": "Cat's eye",
        "donation": "Donate blankets, food"
    }
}

def suggest_remedies(planet_name, severity="medium"):
    """
    Return remedial suggestions for a planet.
    'severity' can influence suggestion strength (not used here).
    """
    return REMEDY_DB.get(planet_name, {"note": "No remedy data available."})

def remedies_for_chart(planet_strengths):
    """
    Given a map of planet strengths (from strengths.planet_strength),
    return a list of suggested remedies for weak/harming planets.
    """
    suggestions = []
    for p in planet_strengths:
        if p.get("is_debilitated") or p.get("is_combust") or p.get("raw_score", 0) < 0:
            suggestions.append({ "planet": p["planet"], "remedy": suggest_remedies(p["planet"]) })
    return suggestions
