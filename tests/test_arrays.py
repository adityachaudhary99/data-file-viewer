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


from python.loaders.arrays import array_page


def test_array_page_2d_window_and_nan_inf_become_null():
    loaded = load_arrays(os.path.join(FX, "arr_2d.npy"))
    res = array_page(loaded.members[0].arr, offset=0, limit=2)
    assert res["columns"] == ["0", "1", "2"]
    assert res["rowCount"] == 4 and res["colCount"] == 3
    assert res["sliced"] is False and res["colsTruncated"] is False
    assert len(res["rows"]) == 2  # limit=2 -> only rows 0..1
    assert res["rows"][0] == [0.0, 1.0, 2.0]
    assert res["rows"][1][1] is None  # NaN at [1,1] -> null


def test_array_page_2d_inf_is_null():
    loaded = load_arrays(os.path.join(FX, "arr_2d.npy"))
    res = array_page(loaded.members[0].arr, offset=2, limit=1)
    assert res["rows"][0][0] is None  # +inf at [2,0] -> null


def test_array_page_1d_is_single_column():
    loaded = load_arrays(os.path.join(FX, "arr_1d.npy"))
    res = array_page(loaded.members[0].arr)
    assert res["columns"] == ["0"]
    assert res["rowCount"] == 10 and res["colCount"] == 1
    assert res["rows"][0] == [0] and res["rows"][9] == [9]


def test_array_page_3d_shows_leading_slice():
    loaded = load_arrays(os.path.join(FX, "arr_3d.npy"))
    res = array_page(loaded.members[0].arr)
    assert res["sliced"] is True
    assert res["sliceLabel"] == "[0, :, :]"
    assert res["rowCount"] == 3 and res["colCount"] == 4  # arr[0] is (3,4)
    assert res["rows"][0] == [0.0, 1.0, 2.0, 3.0]


def test_array_page_scalar_is_one_cell():
    loaded = load_arrays(os.path.join(FX, "arr_scalar.npy"))
    res = array_page(loaded.members[0].arr)
    assert res["rowCount"] == 1 and res["colCount"] == 1
    assert res["rows"] == [[42.0]]


def test_array_page_caps_columns():
    import numpy as np
    wide = np.zeros((2, 250), dtype="float64")
    res = array_page(wide, max_cols=200)
    assert len(res["columns"]) == 200
    assert res["colCount"] == 250 and res["colsTruncated"] is True


from python.loaders.arrays import array_profile, array_raw


def test_array_profile_numeric_counts_nan_inf():
    loaded = load_arrays(os.path.join(FX, "arr_2d.npy"))
    p = array_profile(loaded.members[0].arr)
    assert p["kind"] == "numeric"
    assert p["shape"] == [4, 3] and p["dtype"] == "float64"
    assert p["nanCount"] == 1 and p["infCount"] == 1
    assert p["finite"] == 10
    assert p["min"] == 0.0 and p["max"] == 11.0
    assert p["histogram"]["counts"] and sum(p["histogram"]["counts"]) == 10


def test_array_profile_integer_has_no_nan():
    loaded = load_arrays(os.path.join(FX, "arr_1d.npy"))
    p = array_profile(loaded.members[0].arr)
    assert p["kind"] == "numeric"
    assert p["nanCount"] == 0 and p["infCount"] == 0 and p["finite"] == 10
    assert p["min"] == 0 and p["max"] == 9


def test_array_profile_non_numeric_is_meta_only():
    loaded = load_arrays(os.path.join(FX, "arr_str.npy"))
    p = array_profile(loaded.members[0].arr)
    assert p["kind"] == "non-numeric"
    assert p["size"] == 3 and "histogram" not in p


def test_array_raw_previews_members():
    loaded = load_arrays(os.path.join(FX, "sample.npz"))
    raw = array_raw(loaded, os.path.join(FX, "sample.npz"))
    assert raw["file_type"] == "npz"
    assert [m["name"] for m in raw["members"]] == ["x", "y"]
    assert raw["members"][0]["preview"] == [0, 1, 2, 3, 4, 5]
    assert raw["members"][0]["truncated"] is False
