# ayanamsa.py
from datetime import datetime

def calculate_ayanamsa(date: datetime) -> float:
    """
    Calculate Lahiri Ayanamsa using standard epoch 285 AD.
    """
    y = date.year + (date.month - 1)/12 + (date.day - 1)/365.25
    years_since_epoch = y - 285.0
    arcsec = years_since_epoch * 50.290966
    ayanamsa_deg = arcsec / 3600.0
    return ayanamsa_deg
