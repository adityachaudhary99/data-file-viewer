import os
from dataclasses import dataclass
import numpy as np
from python.jsonsafe import to_jsonable


@dataclass
class LoadedHier:
    nodes: list   # flat pre-order list of node descriptor dicts
    arrays: dict  # leaf path -> np.ndarray


def _leaf_node(path: str, name: str, depth: int, arr) -> dict:
    return {"path": path, "name": name, "kind": "leaf", "depth": depth,
            "shape": [int(d) for d in arr.shape], "dtype": str(arr.dtype)}


def _group_node(path: str, name: str, depth: int) -> dict:
    return {"path": path, "name": name, "kind": "group", "depth": depth}


def _load_h5(path: str) -> LoadedHier:
    import h5py
    nodes: list = []
    arrays: dict = {}

    def walk(group, prefix: str, depth: int):
        for key in group.keys():
            item = group[key]
            p = prefix + "/" + key
            if isinstance(item, h5py.Group):
                nodes.append(_group_node(p, key, depth))
                walk(item, p, depth + 1)
            else:  # h5py.Dataset
                arr = np.asarray(item[()])
                arrays[p] = arr
                nodes.append(_leaf_node(p, key, depth, arr))

    with h5py.File(path, "r") as f:
        walk(f, "", 0)
    return LoadedHier(nodes, arrays)


def _load_nc(path: str) -> LoadedHier:
    from netCDF4 import Dataset
    nodes: list = []
    arrays: dict = {}

    def walk(ds, prefix: str, depth: int):
        for name in ds.variables:
            p = prefix + "/" + name
            arr = np.asarray(ds.variables[name][:])  # MaskedArray -> data (mask-fill best-effort)
            arrays[p] = arr
            nodes.append(_leaf_node(p, name, depth, arr))
        for name in ds.groups:
            p = prefix + "/" + name
            nodes.append(_group_node(p, name, depth))
            walk(ds.groups[name], p, depth + 1)

    ds = Dataset(path, "r")
    try:
        walk(ds, "", 0)
    finally:
        ds.close()
    return LoadedHier(nodes, arrays)


def _load_mat(path: str) -> LoadedHier:
    from scipy.io import loadmat
    from scipy.io.matlab import mat_struct
    nodes: list = []
    arrays: dict = {}

    def walk(items, prefix: str, depth: int):
        for name, value in items:
            p = prefix + "/" + name
            if isinstance(value, mat_struct):
                nodes.append(_group_node(p, name, depth))
                fields = [(fn, getattr(value, fn)) for fn in value._fieldnames]
                walk(fields, p, depth + 1)
            else:
                arr = np.asarray(value)
                arrays[p] = arr
                nodes.append(_leaf_node(p, name, depth, arr))

    data = loadmat(path, squeeze_me=True, struct_as_record=False)
    top = [(k, v) for k, v in data.items() if not k.startswith("__")]
    walk(top, "", 0)
    return LoadedHier(nodes, arrays)


def load_hier(path: str) -> LoadedHier:
    """Load a hierarchical file into (pre-order node list, {leaf path: ndarray}).

    These formats read binary data only — no pickled code is executed (unlike
    .pkl), so no trust prompt is required.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".h5", ".hdf5"):
        return _load_h5(path)
    if ext in (".nc", ".nc4", ".netcdf"):
        return _load_nc(path)
    if ext == ".mat":
        return _load_mat(path)
    raise ValueError(f"load_hier: unsupported extension {ext}")


def node_arr(loaded: "LoadedHier", path):
    """Resolve a leaf path to its ndarray; fall back to the first leaf (pre-order)."""
    if path in loaded.arrays:
        return loaded.arrays[path]
    for n in loaded.nodes:
        if n["kind"] == "leaf":
            return loaded.arrays[n["path"]]
    return None
