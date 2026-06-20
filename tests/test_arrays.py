import os
import numpy as np
import pytest
from python.loaders.arrays import load_arrays, member_meta

FX = os.path.join(os.path.dirname(__file__), "fixtures")


def test_load_npy_single_member():
    loaded = load_arrays(os.path.join(FX, "arr_2d.npy"))
    assert len(loaded.members) == 1
    m = loaded.members[0]
    assert m.name == "array"
    assert m.arr.shape == (4, 3)


def test_load_npz_preserves_member_order():
    loaded = load_arrays(os.path.join(FX, "sample.npz"))
    assert [m.name for m in loaded.members] == ["x", "y"]
    assert loaded.members[1].arr.shape == (3, 2)


def test_member_meta_shape():
    loaded = load_arrays(os.path.join(FX, "arr_2d.npy"))
    meta = member_meta(loaded.members[0].arr)
    assert meta == {"shape": [4, 3], "dtype": "float64", "ndim": 2, "size": 12}


def test_member_meta_scalar():
    loaded = load_arrays(os.path.join(FX, "arr_scalar.npy"))
    meta = member_meta(loaded.members[0].arr)
    assert meta["shape"] == [] and meta["ndim"] == 0 and meta["size"] == 1
