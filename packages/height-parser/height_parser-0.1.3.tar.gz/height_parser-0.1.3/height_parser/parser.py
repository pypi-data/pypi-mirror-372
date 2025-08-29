# height_parser/parser.py  (or yourpkg/height.py)
from __future__ import annotations
from typing import Optional, Union
import re

try:
    import pandas as pd  # for robust isna and Timestamp checks
    _HAS_PANDAS = True
except Exception:
    _HAS_PANDAS = False

MONTH_TO_NUM = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def _is_na(x) -> bool:
    if x is None:
        return True
    s = str(x).strip()
    if s in {"", "-", "0", "NaT"}:
        return True
    if _HAS_PANDAS:
        try:
            if pd.isna(x):
                return True
        except Exception:
            pass
    return False

def _to_cm_or_in(total_inches: float, unit: str) -> float | int:
    unit = unit.lower()
    if unit == "in":
        return int(round(total_inches))
    if unit == "cm":
        return round(total_inches * 2.54, 1)
    raise ValueError("unit must be 'cm' or 'in'")

def _valid_feet_inches(f: int, i: int) -> bool:
    return 3 <= f <= 8 and 0 <= i <= 11

def parse_height(ht_str: Union[str, float, int, None], unit: str = "cm") -> Optional[Union[int, float]]:
    """
    Parse human height from multiple formats:

    1) "F/I/..." or "F-I-..."  (e.g., "6/11/2000", "6-11-2000")
       - If first two tokens are numbers, use them as feet/inches
         if valid; otherwise try swapped (day/month ambiguity).

    2) Excel-like "DD-Mon" (e.g., "11-May", "2-Jun")
       - Month -> feet, Day -> inches.

    3) pandas.Timestamp
       - month -> feet, day -> inches.

    4) Common text formats: "6'11\"", "6 ft 11 in", "6 feet 11 inches"

    Returns:
      height in cm (default) or inches if unit="in"; None if invalid.
    """
    if _is_na(ht_str):
        return None

    # pandas.Timestamp
    if _HAS_PANDAS and isinstance(ht_str, pd.Timestamp):
        f, i = ht_str.month, ht_str.day
        if _valid_feet_inches(f, i):
            return _to_cm_or_in(f * 12 + i, unit)
        return None

    s = str(ht_str).strip()

    # 4) Text formats: 6'11", 6 ft 11 in, etc.
    m = re.fullmatch(r"\s*(\d+)\s*(?:'|ft|feet)\s*(\d+)\s*(?:\"|in|inches)?\s*", s, re.IGNORECASE)
    if m:
        f, i = int(m.group(1)), int(m.group(2))
        if _valid_feet_inches(f, i):
            return _to_cm_or_in(f * 12 + i, unit)

    # 2) "DD-Mon"
    m = re.fullmatch(r"\s*(\d{1,2})-([A-Za-z]{3})\s*", s)
    if m:
        i = int(m.group(1))
        mon = m.group(2).lower()
        f = MONTH_TO_NUM.get(mon)
        if f is not None and _valid_feet_inches(f, i):
            return _to_cm_or_in(f * 12 + i, unit)

    # 1) Delimited numbers, first two tokens as candidates; try swap
    # e.g., "6/11/2000", "11/6/2000", "6-11-2000", "01/06/2000"
    parts = re.split(r"[\/\-]", s)
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        a, b = int(parts[0]), int(parts[1])
        # try as-is
        if _valid_feet_inches(a, b):
            return _to_cm_or_in(a * 12 + b, unit)
        # try swapped (to handle day/month confusion like 01/06 → 6 ft 1 in)
        if _valid_feet_inches(b, a):
            return _to_cm_or_in(b * 12 + a, unit)

    return None

def to_height(series_or_iterable, unit: str = "cm"):
    """
    Vectorized convenience:
      - If input is a pandas Series, returns Series[Float64] with <NA> for missing.
      - Else returns a list (None for invalid).
    """
    try:
        import pandas as pd  # lazy import
        if isinstance(series_or_iterable, pd.Series):
            out = series_or_iterable.apply(lambda x: parse_height(x, unit=unit))
            return out.astype("Float64")
    except Exception:
        pass
    return [parse_height(x, unit=unit) for x in series_or_iterable]
