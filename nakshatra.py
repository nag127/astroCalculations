# nakshatra.py

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshta", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def calculate_nakshatra(moon_sidereal):
    nak_size = 360 / 27
    index = int(moon_sidereal // nak_size)
    portion = (moon_sidereal % nak_size) / nak_size
    pada = int(portion * 4) + 1

    return {
        "nakshatra": NAKSHATRAS[index],
        "nak_index": index,
        "portion_completed": portion,
        "pada": pada
    }
