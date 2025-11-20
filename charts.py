# charts.py
from config import SIGNS


def get_rasi_chart(lagna_deg, planets):
    chart = {i: [] for i in range(1, 13)}
    planet_details = {}

    lagna_sign_index = int(lagna_deg // 30)

    for planet, lon in planets.items():
        sign_index = int(lon // 30)
        house = ((sign_index - lagna_sign_index + 12) % 12) + 1
        chart[house].append(planet)

        planet_details[planet] = {
            "longitude": lon,
            "sign_index": sign_index,
            "sign": SIGNS[sign_index],
            "house": house
        }

    return {
        "houses": chart,
        "planets": planet_details
    }
