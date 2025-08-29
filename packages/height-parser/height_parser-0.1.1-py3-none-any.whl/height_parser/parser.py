from typing import Optional, Union

def parse_height(ht_str: Union[str, float, int, None], unit: str = "cm") -> Optional[Union[int, float]]:
    """
    Convert date-like strings 'F/I/YYYY' (e.g., '6/11/2000') into a height.

    - Interprets first part as feet (F) and second as inches (I).
    - Ignores extra parts (commonly a year).
    - Returns cm by default; unit="in" for inches.
    - Treats "-", "0", or blank as missing (returns None).
    - Sanity checks: feet in [3, 8], inches in [0, 11].
    """
    if ht_str is None:
        return None

    s = str(ht_str).strip()
    if s in {"-", "0", ""}:
        return None

    try:
        parts = [p.strip() for p in s.split("/")]
        if len(parts) < 2:
            return None
        feet, inches = int(parts[0]), int(parts[1])
        if not (3 <= feet <= 8):
            return None
        if not (0 <= inches <= 11):
            return None

        total_inches = feet * 12 + inches
        if unit.lower() == "in":
            return int(total_inches)
        elif unit.lower() == "cm":
            return round(total_inches * 2.54, 1)
        else:
            raise ValueError("unit must be 'cm' or 'in'")
    except Exception:
        return None


def to_height(series_or_iterable, unit: str = "cm"):
    """
    Apply parse_height to a Pandas Series or iterable.
    - Pandas Series → returns Series[Float64] with <NA> for missing.
    - Iterable → returns list.
    """
    try:
        import pandas as pd
        if isinstance(series_or_iterable, pd.Series):
            return series_or_iterable.apply(lambda x: parse_height(x, unit=unit)).astype("Float64")
    except Exception:
        pass
    return [parse_height(x, unit=unit) for x in series_or_iterable]
