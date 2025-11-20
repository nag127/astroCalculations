# houses.py
from skyfield.api import load, Topos
import pytz

def calculate_lagna(dt, lat, lon, tz_str):
    eph = load('de421.bsp')
    earth = eph['Earth']

    tz = pytz.timezone(tz_str)
    local_dt = tz.localize(dt)

    ts = load.timescale()
    t = ts.from_datetime(local_dt)

    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)

    apparent = observer.at(t).from_altaz(alt_degrees=0, az_degrees=90)
    _, lag_lon, _ = apparent.ecliptic_latlon()

    lag_deg = lag_lon.degrees % 360
    signs = [
        "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
    ]

    return {
        "lagna_degree": lag_deg,
        "lagna_sign": signs[int(lag_deg // 30)]
    }
