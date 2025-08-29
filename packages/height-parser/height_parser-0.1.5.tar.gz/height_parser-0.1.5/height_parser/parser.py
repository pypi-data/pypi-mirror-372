import re
from typing import Optional, Union

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False


# ---------------------------
# Month lookup
# ---------------------------
MONTH_TO_NUM = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


# ---------------------------
# Helpers
# ---------------------------
def _is_na(x) -> bool:
    """Check if value is None, empty, dash, or NA-like."""
    if x is None:
        return True
    if isinstance(x, float) and (x != x):  # NaN
        return True
    if isinstance(x, str) and x.strip().lower() in ("", "nan", "na", "-", "none"):
        return True
    return False


def _valid_feet_inches(f: int, i: int) -> bool:
    """Check if plausible feet and inches."""
    return 3 <= f <= 8 and 0 <= i < 12


def _to_cm_or_in(total_inches: int, unit: str = "cm") -> Union[float, int]:
    """Convert inches to desired unit."""
    if unit == "cm":
        return round(total_inches * 2.54, 1)
    return total_inches


# ---------------------------
# Core parser
# ---------------------------
def parse_height(ht_str: Union[str, float, int, None], unit: str = "cm") -> Optional[Union[int, float]]:
    """
    Parse a string like '11-May', '2-Jun', '11/05/2025', '03/06/2025'
    into a numeric height in cm (default) or inches.
    """
    if _is_na(ht_str):
        return pd.NA if _HAS_PANDAS else None

    # If pandas Timestamp
    if _HAS_PANDAS and isinstance(ht_str, pd.Timestamp):
        f, i = ht_str.month, ht_str.day
        if _valid_feet_inches(f, i):
            return _to_cm_or_in(f * 12 + i, unit)
        return pd.NA if _HAS_PANDAS else None

    s = str(ht_str).strip()

    # --- Case 1: "DD-Mon" (e.g., "11-May", "2-Jun")
    m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})", s, re.IGNORECASE)
    if m:
        i = int(m.group(1))
        mon = m.group(2).lower()
        f = MONTH_TO_NUM.get(mon)
        if f is not None and _valid_feet_inches(f, i):
            return _to_cm_or_in(f * 12 + i, unit)
        return pd.NA if _HAS_PANDAS else None

    # --- Case 2: "DD/MM/YYYY" or "DD-MM-YYYY"
    parts = re.split(r"[\/\-]", s)
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        d, mth = int(parts[0]), int(parts[1])
        # Prefer month as feet, day as inches
        if _valid_feet_inches(mth, d):
            return _to_cm_or_in(mth * 12 + d, unit)
        if _valid_feet_inches(d, mth):
            return _to_cm_or_in(d * 12 + mth, unit)

    return pd.NA if _HAS_PANDAS else None


# ---------------------------
# Vectorized interface
# ---------------------------
def to_height(series_or_iterable, unit: str = "cm"):
    """
    Vectorized convenience:
      - If input is a pandas Series, returns Series with <NA> for missing.
      - Else returns a list (None for invalid).
    """
    try:
        import pandas as pd
        if isinstance(series_or_iterable, pd.Series):
            return series_or_iterable.apply(lambda x: parse_height(x, unit=unit))
    except Exception:
        pass
    return [parse_height(x, unit=unit) for x in series_or_iterable]
