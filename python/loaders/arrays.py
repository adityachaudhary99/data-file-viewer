import os
from dataclasses import dataclass
import numpy as np
import pandas as pd
from python.jsonsafe import to_jsonable
from python.profiler import histogram


@dataclass
class ArrayMember:
    name: str
    arr: np.ndarray


@dataclass
class LoadedArrays:
    members: list  # list[ArrayMember]


def load_arrays(path: str) -> LoadedArrays:
    """Load a .npy (single array) or .npz (named archive) with pickle DISABLED.

    allow_pickle=False is a security guarantee: object-dtype arrays are stored
    as pickles and would execute code on load. Such files raise here and the
    session surfaces a clean error instead of running untrusted code.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".npy":
        arr = np.load(path, allow_pickle=False)
        return LoadedArrays([ArrayMember("array", arr)])
    if ext == ".npz":
        with np.load(path, allow_pickle=False) as npz:
            members = [ArrayMember(name, npz[name]) for name in npz.files]
        return LoadedArrays(members)
    raise ValueError(f"load_arrays: unsupported extension {ext}")


def member_meta(arr) -> dict:
    return {
        "shape": [int(d) for d in arr.shape],
        "dtype": str(arr.dtype),
        "ndim": int(arr.ndim),
        "size": int(arr.size),
    }


def _to_2d(arr):
    """Return (view2d, sliced, slice_label) — a 2-D array to display."""
    if arr.ndim == 0:
        return arr.reshape(1, 1), False, ""
    if arr.ndim == 1:
        return arr.reshape(-1, 1), False, ""
    if arr.ndim == 2:
        return arr, False, ""
    lead = arr.ndim - 2
    label = "[" + ", ".join(["0"] * lead + [":", ":"]) + "]"
    return arr[(0,) * lead], True, label


def _is_numeric(arr) -> bool:
    return np.issubdtype(arr.dtype, np.integer) or np.issubdtype(arr.dtype, np.floating)


def array_profile(arr, bins: int = 20) -> dict:
    out = member_meta(arr)
    if not _is_numeric(arr):
        out["kind"] = "non-numeric"
        return out
    out["kind"] = "numeric"
    flat = np.asarray(arr).ravel()
    if np.issubdtype(arr.dtype, np.floating):
        nan_count = int(np.isnan(flat).sum())
        inf_count = int(np.isinf(flat).sum())
    else:
        nan_count = inf_count = 0
    finite = flat[np.isfinite(flat)]
    out["nanCount"] = nan_count
    out["infCount"] = inf_count
    out["finite"] = int(finite.size)
    if finite.size:
        out["min"] = to_jsonable(finite.min())
        out["max"] = to_jsonable(finite.max())
        out["mean"] = to_jsonable(finite.mean())
        out["std"] = to_jsonable(finite.std())
    else:
        out["min"] = out["max"] = out["mean"] = out["std"] = None
    out["histogram"] = histogram(pd.Series(finite), bins)
    return out


def array_raw(loaded: "LoadedArrays", path: str) -> dict:
    members = []
    for m in loaded.members:
        flat = np.asarray(m.arr).ravel()
        preview = [to_jsonable(v) for v in flat[:100]]
        members.append({
            "name": m.name,
            "shape": [int(d) for d in m.arr.shape],
            "dtype": str(m.arr.dtype),
            "size": int(m.arr.size),
            "preview": preview,
            "truncated": int(m.arr.size) > 100,
        })
    return {"file_type": os.path.splitext(path)[1].lstrip("."), "members": members}


def array_page(arr, offset: int = 0, limit: int = 200, max_cols: int = 200) -> dict:
    view, sliced, slice_label = _to_2d(arr)
    nrows, ncols = int(view.shape[0]), int(view.shape[1])
    show_cols = min(ncols, max_cols)
    window = view[offset: offset + limit, :show_cols]
    rows = [[to_jsonable(v) for v in row] for row in window]
    return {
        "columns": [str(c) for c in range(show_cols)],
        "rows": rows,
        "rowCount": nrows,
        "colCount": ncols,
        "colsTruncated": ncols > show_cols,
        "sliced": sliced,
        "sliceLabel": slice_label,
    }
