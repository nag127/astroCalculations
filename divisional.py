# divisional.py
# Compute D9 (Navamsa), D10 (Dasamsa), D7 (Saptamsa) divisional longitudes and sign

from config import SIGNS

def divisional_longitude(longitude_deg, N):
    """
    General divisional calculator.
    Algorithm:
    - sign_index = int(longitude_deg // 30)
    - offset = longitude_deg % 30
    - part_size = 30 / N
    - part_index = int(offset // part_size)  # 0..N-1
    - divisional_sign_index = (sign_index * N + part_index) % 12
    - divisional_offset = (offset % part_size) * N
    - divisional_long = divisional_sign_index*30 + divisional_offset
    This gives a divisional longitude (0..360)
    """
    sign_index = int(longitude_deg // 30)
    offset = longitude_deg % 30
    part_size = 30.0 / N
    part_index = int(offset // part_size)
    divisional_sign_index = (sign_index * N + part_index) % 12
    # offset within the part scaled to 0..30
    divisional_offset = (offset - part_index * part_size) * (N)
    divisional_long = (divisional_sign_index * 30.0 + divisional_offset) % 360
    return divisional_long

def navamsa(longitude_deg):
    """D9"""
    d9 = divisional_longitude(longitude_deg, 9)
    sign_idx = int(d9 // 30)
    return {"d9_longitude": d9, "d9_sign": SIGNS[sign_idx], "d9_offset": d9 % 30}

def dasamsa(longitude_deg):
    """D10"""
    d10 = divisional_longitude(longitude_deg, 10)
    sign_idx = int(d10 // 30)
    return {"d10_longitude": d10, "d10_sign": SIGNS[sign_idx], "d10_offset": d10 % 30}

def saptamsa(longitude_deg):
    """D7"""
    d7 = divisional_longitude(longitude_deg, 7)
    sign_idx = int(d7 // 30)
    return {"d7_longitude": d7, "d7_sign": SIGNS[sign_idx], "d7_offset": d7 % 30}
