# panchanga.py
def calculate_panchanga(sun_lon, moon_lon):
    tithi = int(((moon_lon - sun_lon + 360) % 360) / 12)

    yoga = int(((sun_lon + moon_lon) % 360) / 13.3333)

    karana = (tithi * 2) % 60

    return {
        "tithi": tithi,
        "yoga": yoga,
        "karana": karana
    }
