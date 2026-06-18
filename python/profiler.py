import numpy as np
import pandas as pd
from python.jsonsafe import to_jsonable

HIGH_NULL = 0.30
HIGH_CARD_RATIO = 0.9


def histogram(series, bins: int = 20) -> dict:
    vals = pd.to_numeric(series, errors="coerce").dropna().to_numpy()
    if vals.size == 0:
        return {"edges": [], "counts": []}
    counts, edges = np.histogram(vals, bins=bins)
    return {"edges": [float(e) for e in edges], "counts": [int(c) for c in counts]}


def _flags(nulls: int, total: int, unique: int) -> dict:
    non_null = total - nulls
    return {
        "highNull": (nulls / total) >= HIGH_NULL if total else False,
        "constant": unique <= 1,
        "highCardinality": non_null > 0 and unique >= HIGH_CARD_RATIO * non_null,
    }


def profile_column(series: pd.Series) -> dict:
    total = int(len(series))
    nulls = int(series.isna().sum())
    unique = int(series.nunique(dropna=True))
    out = {
        "dtype": str(series.dtype),
        "count": total,
        "nulls": nulls,
        "nullPct": (nulls / total) if total else 0.0,
        "unique": unique,
        "flags": _flags(nulls, total, unique),
    }
    if pd.api.types.is_bool_dtype(series):
        out["kind"] = "boolean"
        out["trueCount"] = int((series == True).sum())  # noqa: E712
        out["falseCount"] = int((series == False).sum())  # noqa: E712
    elif pd.api.types.is_numeric_dtype(series):
        out["kind"] = "numeric"
        desc = series.describe()
        out["min"] = to_jsonable(series.min())
        out["max"] = to_jsonable(series.max())
        out["mean"] = to_jsonable(series.mean())
        out["std"] = to_jsonable(series.std())
        out["q25"] = to_jsonable(desc.get("25%"))
        out["q50"] = to_jsonable(desc.get("50%"))
        out["q75"] = to_jsonable(desc.get("75%"))
        out["histogram"] = histogram(series)
    else:
        out["kind"] = "categorical"
        vc = series.value_counts(dropna=True).head(10)
        out["top"] = [{"value": to_jsonable(k), "count": int(v)} for k, v in vc.items()]
    return out
