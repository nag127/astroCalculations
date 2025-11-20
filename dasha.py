# dasha.py
# Full Vimshottari Dasha calculator (Mahadasha, Antardasha, Pratyantardasha)

from datetime import datetime, timedelta

# Vimshottari Dasha order
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Vimshottari Dasha durations (in years)
DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}


# ---------------------------------------------------
# Dasha Balance At Birth
# ---------------------------------------------------
def get_dasha_balance_at_birth(moon_sidereal_deg):
    nak_size = 360 / 27
    nak_index = int(moon_sidereal_deg // nak_size)

    start_lord = DASHA_ORDER[nak_index % 9]

    portion_completed = (moon_sidereal_deg % nak_size) / nak_size
    portion_remaining = 1 - portion_completed

    total_years = DASHA_YEARS[start_lord]
    remaining_years = total_years * portion_remaining

    years = int(remaining_years)
    months = int((remaining_years - years) * 12)
    days = int((((remaining_years - years) * 12) - months) * 30.44)

    return {
        "starting_mahadasha": start_lord,
        "remaining_years_exact": remaining_years,
        "years": years,
        "months": months,
        "days": days,
        "portion_completed_percent": round(portion_completed * 100, 4),
        "portion_remaining_percent": round(portion_remaining * 100, 4),
    }


# ---------------------------------------------------
# Add years-months-days to datetime
# ---------------------------------------------------
def add_years_months_days(dt, years, months, days):
    total_days = int(years * 365.25 + months * 30.44 + days)
    return dt + timedelta(days=total_days)


# ---------------------------------------------------
# Compute Full Mahadashas (9 Lords)
# ---------------------------------------------------
def compute_mahadashas(starting_lord, birth_dt):
    md_list = []
    idx = DASHA_ORDER.index(starting_lord)

    # First: only the remaining balance from birth
    bal = get_dasha_balance_at_birth_mini(birth_dt, starting_lord)
    md_list.append(bal)

    # Next: full cycles
    for i in range(1, 9):
        lord = DASHA_ORDER[(idx + i) % 9]
        start = md_list[-1]["end"]
        duration = DASHA_YEARS[lord]

        end = add_years_months_days(start, duration, 0, 0)

        md_list.append({
            "mahadasha": lord,
            "start": start,
            "end": end,
            "years": duration
        })

    return md_list


# Helper for first Mahadasha only
def get_dasha_balance_at_birth_mini(birth_dt, lord):
    bal = get_dasha_balance_at_birth(0)  # dummy, replaced below
    # direct override
    import copy
    bal = copy.deepcopy(bal)
    bal["mahadasha"] = lord
    years = bal["years"]
    months = bal["months"]
    days = bal["days"]

    start = birth_dt
    end = add_years_months_days(start, years, months, days)

    return {
        "mahadasha": lord,
        "start": start,
        "end": end,
        "years": years,
        "months": months,
        "days": days,
    }


# ---------------------------------------------------
# Antardasha (sub-periods)
# ---------------------------------------------------
def compute_antardashas(maha_lord, start, end):
    result = []

    total_days = (end - start).days
    maha_years = DASHA_YEARS[maha_lord]

    for lord in DASHA_ORDER:
        antar_fraction = DASHA_YEARS[lord] / 120.0
        dur_days = int(total_days * antar_fraction)

        antar_start = start if not result else result[-1]["end"]
        antar_end = antar_start + timedelta(days=dur_days)

        result.append({
            "mahadasha": maha_lord,
            "antardasha": lord,
            "start": antar_start,
            "end": antar_end
        })

    return result


# ---------------------------------------------------
# Pratyantardasha (sub-sub-periods)
# ---------------------------------------------------
def compute_pratyantardashas(maha_lord, antar_lord, start, end):
    result = []

    total_days = (end - start).days

    for lord in DASHA_ORDER:
        frac = DASHA_YEARS[lord] / 120.0
        dur_days = int(total_days * frac)

        p_start = start if not result else result[-1]["end"]
        p_end = p_start + timedelta(days=dur_days)

        result.append({
            "mahadasha": maha_lord,
            "antardasha": antar_lord,
            "pratyantardasha": lord,
            "start": p_start,
            "end": p_end
        })

    return result


# ---------------------------------------------------
# FULL TREE BUILDER (used by astrology_full.py)
# ---------------------------------------------------
def build_full_dasha_tree(starting_lord, birth_dt, moon_sidereal):
    """
    Returns:
    [
       {
          "mahadasha": { ... },
          "antardashas": [
                {
                    "antardasha": {...},
                    "pratyantardashas": [...]
                }
          ]
       }
    ]
    """
    md_list = compute_mahadashas(starting_lord, birth_dt)

    full = []

    for md in md_list:
        maha_lord = md["mahadasha"]
        antars = compute_antardashas(maha_lord, md["start"], md["end"])

        antar_list = []
        for ad in antars:
            praty = compute_pratyantardashas(
                maha_lord,
                ad["antardasha"],
                ad["start"],
                ad["end"],
            )

            antar_list.append({
                "antardasha": ad,
                "pratyantardashas": praty
            })

        full.append({
            "mahadasha": md,
            "antardashas": antar_list
        })

    return full
