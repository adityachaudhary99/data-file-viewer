import datetime
import math
import numpy as np
import pandas as pd


def to_jsonable(value):
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode("utf-8", "replace")
    if isinstance(value, (np.ndarray, list, tuple)):
        # Arrow list / fixed_size_list columns arrive from to_pandas() as ndarray cells
        return [to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, np.floating) and value.dtype.itemsize < 8:
        # shortest repr, so float32 0.1 shows as 0.1 rather than 0.10000000149011612
        value = float(str(value))
    if isinstance(value, np.datetime64):
        value = pd.Timestamp(value)  # .item() would return an int for ns precision
    elif isinstance(value, np.timedelta64):
        value = pd.Timedelta(value)
    if value is pd.NaT:
        return None
    if isinstance(value, (datetime.date, datetime.time, datetime.timedelta)):
        return str(value)  # also covers pd.Timestamp / pd.Timedelta (subclasses)
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, complex):
        r = value.real if math.isfinite(value.real) else None
        i = value.imag if math.isfinite(value.imag) else None
        rs = "nan" if r is None else f"{r:g}"
        isn = "nan" if i is None else f"{i:+g}"
        return f"{rs}{isn}j"
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    try:
        if value is pd.NaT or (pd.isna(value) and not isinstance(value, (list, dict))):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (str, int, float, bool, list, dict)):
        return value
    return str(value)  # Decimal, UUID, ...: keep the row displayable


def as_hashable(series):
    """Map array cells to flat tuples so sort_values / nunique / value_counts work on them."""
    if series.dtype != object:
        return series
    return series.map(lambda v: tuple(to_jsonable(x) for x in np.asarray(v).ravel())
                      if isinstance(v, (np.ndarray, list, tuple)) else v)
