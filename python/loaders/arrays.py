import os
from dataclasses import dataclass
import numpy as np


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
