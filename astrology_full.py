# astrology_full.py

from datetime import datetime

# Basic components
from astronomy import get_moon_longitude, get_sidereal_planets, calculate_lagna
from ayanamsa import calculate_ayanamsa
from nakshatra_utils import get_nakshatra

# Charts
from charts import get_rasi_chart

# Dasha modules
from dasha import (
    get_dasha_balance_at_birth,
    build_full_dasha_tree
)

# Panchanga
from panchanga import calculate_panchanga

# Strengths, Yogas, Remedies
from strengths import planet_strength
from yogas import detect_yogas
from remedies import remedies_for_chart

# Divisional charts (Navamsa, Dasamsa, Saptamsa)
from divisional import navamsa, dasamsa, saptamsa

# Transits (Gochar)
from transits import current_transits, transit_vs_natal, sade_sati


def astrology_full(dob, tob, tz_str, latitude, longitude):

    # Normalize variable names
    lat = latitude
    lon = longitude
    # ----------------------------------------------------------
    dt = datetime.strptime(dob + " " + tob, "%Y-%m-%d %H:%M")
    ayan = calculate_ayanamsa(dt)

    # ----------------------------------------------------------
    # 2️⃣ Moon Tropical & Sidereal
    # ----------------------------------------------------------
    moon_lon_trop = get_moon_longitude(dt, lat, lon, tz_str)
    moon_sidereal = (moon_lon_trop - ayan) % 360

    # ----------------------------------------------------------
    # 3️⃣ Nakshatra
    # ----------------------------------------------------------
    nak = get_nakshatra(moon_sidereal)

    # ----------------------------------------------------------
    # 4️⃣ Lagna (Ascendant)
    # ----------------------------------------------------------
    lagna_deg = calculate_lagna(dt, lat, lon, tz_str)
    lagna = {
        "degree": lagna_deg,
        "sign_index": int(lagna_deg // 30)
    }

    # ----------------------------------------------------------
    # 5️⃣ Sidereal Planets
    # ----------------------------------------------------------
    planets = get_sidereal_planets(dt, lat, lon, tz_str)

    # ----------------------------------------------------------
    # 6️⃣ Rasi Chart (12 houses)
    # ----------------------------------------------------------
    rasi_chart = get_rasi_chart(lagna_deg, planets)

    # ----------------------------------------------------------
    # 7️⃣ Panchanga (tithi, yoga, karana, weekday)
    # ----------------------------------------------------------
    panchanga = calculate_panchanga(planets["Sun"], planets["Moon"])

    # ----------------------------------------------------------
    # 8️⃣ Vimshottari Dasha
    # ----------------------------------------------------------
    dasha_balance = get_dasha_balance_at_birth(moon_sidereal)
    full_dasha = build_full_dasha_tree(
        dasha_balance["starting_mahadasha"],
        dt,
        moon_sidereal
    )

    # ----------------------------------------------------------
    # 9️⃣ Planet Strength Evaluation
    # ----------------------------------------------------------
    planet_strength_list = []
    for name, lon in planets.items():
        ps = planet_strength(name, lon, sun_longitude=planets["Sun"])
        planet_strength_list.append(ps)

    # ----------------------------------------------------------
    # 🔟 Yogas (Gajakesari, Mahapurush, Kemadruma, etc.)
    # ----------------------------------------------------------
    yogas = detect_yogas(rasi_chart["planets"])

    # ----------------------------------------------------------
    # 1️⃣1️⃣ Divisional Charts (Navamsa D9, Dasamsa D10, Saptamsa D7)
    # ----------------------------------------------------------
    divisional = {
        name: {
            "D9": navamsa(lon),
            "D10": dasamsa(lon),
            "D7": saptamsa(lon)
        }
        for name, lon in planets.items()
    }

    # ----------------------------------------------------------
    # 1️⃣2️⃣ Remedies Based on Strength
    # ----------------------------------------------------------
    remedies = remedies_for_chart(planet_strength_list)

    # ----------------------------------------------------------
    # 1️⃣3️⃣ Transit (Gochar) & Sade Sati
    # ----------------------------------------------------------
    transit_planets = current_transits(datetime.now(), lat, lon, tz_str)
    transit_comparison = transit_vs_natal(planets, transit_planets)

    sade_sati_status = sade_sati(
        natal_moon_lon=moon_sidereal,
        saturn_transit_lon=transit_planets["Saturn"]
    )

    # ----------------------------------------------------------
    # FINAL RESPONSE
    # ----------------------------------------------------------
    return {
        "meta": {
            "dob": dob,
            "tob": tob,
            "timezone": tz_str,
            "latitude": lat,
            "longitude": lon
        },

        "ayanamsa": ayan,

        "moon": {
            "tropical": moon_lon_trop,
            "sidereal": moon_sidereal,
            "nakshatra": nak
        },

        "lagna": lagna,

        "planets": planets,

        "rasi_chart": rasi_chart,

        "panchanga": panchanga,

        "dasha": {
            "balance": dasha_balance,
            "dv": full_dasha
        },

        "strengths": planet_strength_list,

        "yogas": yogas,

        "divisional": divisional,

        "remedies": remedies,

        "transits": {
            "current": transit_planets,
            "comparison": transit_comparison,
            "sade_sati": sade_sati_status
        }
    }
