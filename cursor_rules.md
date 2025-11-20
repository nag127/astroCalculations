# Vedic Astrology Project Rules

1. Use DE421 ephemeris for all planet, moon, and earth calculations.
2. Use Lahiri ayanamsa for sidereal conversion.
3. Keep astronomy.py clean and accurate:
    - tropical → sidereal conversion
    - topocentric longitudes
    - ascendant (lagna) calculation
4. All astrology modules must use sidereal degrees.
5. Ensure dasha logic follows Vimshottari:
    - Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury
6. Divisional charts must use simple modular arithmetic:
    - D9 Navamsa
    - D10 Dasamsa
    - D7 Saptamsa
7. Ensure rasi chart uses lagna as first house and wraps around 12 signs.
8. Ensure panchanga: tithi, yoga, karana, weekday.
9. Transits: use sidereal transits and compare to natal chart.
10. All modules should return clean JSON-ready dictionaries.
