# yourpkg/height.py
from typing import Optional, Union
import re

try:
    import pandas as pd
    _HAS_PANDAS = True
except Exception:
    _HAS_PANDAS = False

MONTH_TO_NUM = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def _to_cm_or_in(total_inches: int | float, unit: str) -> float | int:
    if unit.lower() == "in":
        return int(total_inches)
    if unit.lower() == "cm":
        return round(total_inches * 2.54, 1)
    raise ValueError("unit must be 'cm' or 'in'")

def parse_height(ht_str: Union[str, float, int, None], unit: str = "cm") -> Optional[Union[int, float]]:
    """
    Parse human height from a few common formats:

    1) "F/I/YYYY" or "F/I/..." (e.g., "6/1/2000")  -> feet/inches(/ignored)
       - Interprets first part as feet, second as inches.
    2) Excel-mangled dates "DD-Mon" strings (e.g., "11-May", "2-Jun")
       - Interprets MONTH as feet (May=5, Jun=6), DAY as inches.
    3) pandas.Timestamp (if column was parsed as real datetimes)
       - Uses month as feet, day as inches.

    Returns:
      - height in cm (default) or inches if unit="in"
      - None for "-", "0", "", invalid, or out-of-range values
    """
    # Missing
    if ht_str is None:
        return None

    # Handle pandas NaN
    if _HAS_PANDAS and isinstance(ht_str, float) and pd.isna(ht_str):
        return None

    s = str(ht_str).strip()
    if s in {"-", "0", ""}:
        return None

    feet = inches = None

    # Case A: classic "F/I/..."
    # Accept separators / or - just in case ("6/1/2000", "6-1-2000")
    # NOTE: We only care about first two numbers.
    parts = re.split(r"[\/\-]", s)
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        f = int(parts[0])
        i = int(parts[1])
        if 3 <= f <= 8 and 0 <= i <= 11:
            feet, inches = f, i

    # Case B: Excel-like "DD-Mon" (e.g., "11-May", "2-Jun")
    if feet is None:
        m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})", s)
        if m:
            i = int(m.group(1))
            mon = m.group(2).lower()
            f = MONTH_TO_NUM.get(mon)
            if f is not None and 3 <= f <= 8 and 0 <= i <= 11:
                feet, inches = f, i

    # Case C: pandas.Timestamp -> use month as feet, day as inches
    if feet is None and _HAS_PANDAS and isinstance(ht_str, pd.Timestamp):
        f = ht_str.month
        i = ht_str.day
        if 3 <= f <= 8 and 0 <= i <= 11:
            feet, inches = f, i

    if feet is None:
        return None

    total_inches = feet * 12 + inches
    return _to_cm_or_in(total_inches, unit)
