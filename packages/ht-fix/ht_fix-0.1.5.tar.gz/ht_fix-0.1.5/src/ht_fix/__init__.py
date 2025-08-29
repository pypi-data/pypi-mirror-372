# src/ht_fix/height.py
import re
import math
from typing import Any, Iterable, Union

__all__ = ["parse_height", "clamp_inches", "fix_height"]

# Map Excel-mangled month tokens to FEET (e.g., "4-Jun" == 6'4")
_MON2FEET = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def _to_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return math.nan

def parse_height(x: Any) -> float:
    """
    Parse a single height value into inches.
    Returns NaN when unparseable.

    Handles:
      - "6-7", "6'7", "6 ft 7", "6’7"
      - "200 cm", "72", "72 in"
      - Excel-like: "4-Jun" (6'4), "Jun-00" (6'0), "11-May" (5'11), "1-Jul" (7'1)
    """
    if x is None:
        return math.nan

    s = str(x).strip()
    if s == "" or s in {"-", "—", "nan", "None"}:
        return math.nan

    # Excel-like encodings
    m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})", s)  # D-Mon
    if m:
        inch = int(m.group(1))
        feet = _MON2FEET.get(m.group(2).lower())
        if feet is not None:
            return feet * 12 + inch

    m = re.fullmatch(r"([A-Za-z]{3})-(\d{1,2})", s)  # Mon-D or Mon-00
    if m:
        feet = _MON2FEET.get(m.group(1).lower())
        inch = int(m.group(2))
        if feet is not None:
            return feet * 12 + inch

    # Foot-inch forms
    m = re.fullmatch(r"\s*(\d{1,2})\s*(?:-|\'|′|’|ft)\s*(\d{1,2})?\s*", s)
    if m:
        feet = int(m.group(1))
        inch = int(m.group(2) or 0)
        return feet * 12 + inch

    # With units: "200 cm", "72 in"
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(cm|in|inch|inches)?\s*", s, flags=re.I)
    if m:
        v = float(m.group(1))
        unit = (m.group(2) or "").lower()
        if unit in {"in", "inch", "inches"}:
            return v
        if unit == "cm":
            return v / 2.54
        # no unit: assume inches unless too large (then cm)
        return v / 2.54 if v > 100 else v

    # Plain number fallback
    v = _to_float(s)
    if not math.isnan(v):
        return v / 2.54 if v > 100 else v

    return math.nan

def clamp_inches(value: Union[float, int], min_inches: int = 60, max_inches: int = 96) -> float:
    """Clamp inch value to [min_inches, max_inches]; out-of-range -> NaN."""
    v = _to_float(value)
    if math.isnan(v):
        return math.nan
    return v if (min_inches <= v <= max_inches) else math.nan

def fix_height(obj: Any, min_feet: int = 5, max_feet: int = 8):
    """
    Convert heights to inches and clamp to [min_feet, max_feet].
    Works on scalars, iterables, and pandas Series (if pandas is installed).
    """
    min_inches = int(min_feet * 12)
    max_inches = int(max_feet * 12)

    # Pandas Series support (optional)
    try:
        import pandas as pd  # type: ignore
        if isinstance(obj, pd.Series):
            out = obj.apply(parse_height).astype("float64")
            return out.apply(lambda v: clamp_inches(v, min_inches, max_inches))
    except Exception:
        pass

    # Iterable
    if isinstance(obj, (list, tuple)):
        return [clamp_inches(parse_height(v), min_inches, max_inches) for v in obj]

    # Scalar
    return clamp_inches(parse_height(obj), min_inches, max_inches)
