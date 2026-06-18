import math
import numpy as np
import pandas as pd


def to_jsonable(value):
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode("utf-8", "replace")
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    try:
        if value is pd.NaT or (pd.isna(value) and not isinstance(value, (list, dict))):
            return None
    except (TypeError, ValueError):
        pass
    return value
