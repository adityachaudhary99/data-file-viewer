import os
from dataclasses import dataclass
import numpy as np
from python.jsonsafe import to_jsonable


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
