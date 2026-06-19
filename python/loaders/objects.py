import os
import pickle
from dataclasses import dataclass
import pandas as pd

from python.loaders.tabular import LoadedTable
from python.convert_pkl import convert_to_serializable as _pkl_to_json
from python.convert_msgpack import convert_to_serializable as _mp_to_json


@dataclass
class AutoLoaded:
    kind: str            # "tabular" | "object"
    table: LoadedTable | None
    obj_json: dict | None


def _as_tabular(df: pd.DataFrame, max_rows: int) -> AutoLoaded:
    total = len(df)
    capped = df.head(max_rows) if total > max_rows else df
    return AutoLoaded("tabular", LoadedTable(df=capped, sampled=total > max_rows, total=total), None)


def load_auto(path: str, max_rows: int = 200_000) -> AutoLoaded:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".pkl", ".pickle", ".joblib"):
        if ext == ".joblib":
            import joblib
            obj = joblib.load(path)
        else:
            with open(path, "rb") as f:
                obj = pickle.load(f)
        if isinstance(obj, pd.DataFrame):
            return _as_tabular(obj, max_rows)
        if isinstance(obj, pd.Series):
            return _as_tabular(obj.to_frame(), max_rows)
        return AutoLoaded("object", None, {"file_type": ext.lstrip("."), "data": _pkl_to_json(obj)})
    if ext in (".msgpack", ".mp"):
        import msgpack
        with open(path, "rb") as f:
            obj = msgpack.unpack(f, raw=False, strict_map_key=False)
        if isinstance(obj, list) and obj and all(isinstance(r, dict) for r in obj):
            return _as_tabular(pd.DataFrame(obj), max_rows)
        return AutoLoaded("object", None, {"file_type": "msgpack", "data": _mp_to_json(obj)})
    raise ValueError(f"load_auto: unsupported extension {ext}")
