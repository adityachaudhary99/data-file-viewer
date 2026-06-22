import os
import numpy as np
from python.loaders.arrays import array_page, array_profile
from python.loaders.hierarchical import load_hier, node_arr, hier_raw

FX = os.path.join(os.path.dirname(__file__), "fixtures")


def test_h5_preorder_tree_and_kinds():
    loaded = load_hier(os.path.join(FX, "sample.h5"))
    rows = [(n["path"], n["kind"], n["depth"]) for n in loaded.nodes]
    # h5py iterates keys alphabetically -> grp, grp/values, ids, labels
    assert rows == [
        ("/grp", "group", 0),
        ("/grp/values", "leaf", 1),
        ("/ids", "leaf", 0),
        ("/labels", "leaf", 0),
    ]


def test_h5_leaf_meta_and_arrays():
    loaded = load_hier(os.path.join(FX, "sample.h5"))
    by_path = {n["path"]: n for n in loaded.nodes}
    assert by_path["/grp/values"]["shape"] == [3, 4]
    assert by_path["/grp/values"]["dtype"] == "float64"
    assert by_path["/ids"]["shape"] == [5]
    assert "shape" not in by_path["/grp"]           # group has no shape/dtype
    assert set(loaded.arrays) == {"/grp/values", "/ids", "/labels"}
    assert np.isnan(loaded.arrays["/grp/values"][0, 0])


def test_node_arr_resolves_and_falls_back():
    loaded = load_hier(os.path.join(FX, "sample.h5"))
    assert node_arr(loaded, "/ids").tolist() == [0, 1, 2, 3, 4]
    # unknown path -> first leaf in pre-order (/grp/values)
    first = node_arr(loaded, "/does/not/exist")
    assert first.shape == (3, 4)


def test_nc_variables_then_groups():
    loaded = load_hier(os.path.join(FX, "sample.nc"))
    rows = [(n["path"], n["kind"], n["depth"]) for n in loaded.nodes]
    # root variables first (creation order), then nested groups
    assert rows == [
        ("/temp", "leaf", 0),
        ("/pressure", "leaf", 0),
        ("/region", "group", 0),
        ("/region/rid", "leaf", 1),
    ]
    assert loaded.arrays["/temp"].tolist() == [10.0, 11.5, 9.0, 12.0]
    assert loaded.arrays["/region/rid"].tolist() == [1, 2, 3]


def test_mat_arrays_and_struct_group():
    loaded = load_hier(os.path.join(FX, "sample.mat"))
    by = {n["path"]: n for n in loaded.nodes}
    # struct "params" becomes a group; its fields become leaves
    assert by["/params"]["kind"] == "group"
    assert by["/params/a"]["kind"] == "leaf"
    assert by["/params/b"]["shape"] == [3]
    assert by["/matrix"]["shape"] == [2, 3]
    assert by["/vector"]["shape"] == [4]
    assert "/matrix" in loaded.arrays and "/params/b" in loaded.arrays
    assert loaded.arrays["/matrix"].shape == (2, 3)


def test_leaf_reuses_array_page_and_profile():
    loaded = load_hier(os.path.join(FX, "sample.h5"))
    page = array_page(node_arr(loaded, "/grp/values"))
    assert page["columns"] == ["0", "1", "2", "3"]
    assert page["rowCount"] == 3 and page["colCount"] == 4
    assert page["rows"][0][0] is None       # NaN at [0,0] -> null
    prof = array_profile(node_arr(loaded, "/ids"))
    assert prof["kind"] == "numeric" and prof["min"] == 0 and prof["max"] == 4


def test_hier_raw_lists_nodes_with_leaf_previews():
    loaded = load_hier(os.path.join(FX, "sample.h5"))
    raw = hier_raw(loaded, os.path.join(FX, "sample.h5"))
    assert raw["file_type"] == "h5"
    by = {n["path"]: n for n in raw["nodes"]}
    assert by["/grp"]["kind"] == "group" and "preview" not in by["/grp"]
    assert by["/ids"]["preview"] == [0, 1, 2, 3, 4]
    assert by["/ids"]["truncated"] is False
    assert by["/grp/values"]["preview"][0] is None   # NaN -> null via to_jsonable


def test_nc_masked_fill_becomes_nan(tmp_path):
    from netCDF4 import Dataset
    p = tmp_path / "m.nc"
    ds = Dataset(str(p), "w")
    ds.createDimension("x", 3)
    v = ds.createVariable("t", "f8", ("x",), fill_value=9.0e36)
    v[:] = np.ma.array([1.0, 2.0, 3.0], mask=[False, True, False])
    ds.close()
    loaded = load_hier(str(p))
    arr = node_arr(loaded, "/t")
    assert np.isnan(arr[1]) and arr[0] == 1.0 and arr[2] == 3.0

def test_mat_sparse_densifies(tmp_path):
    import json
    import scipy.sparse as sp
    from scipy.io import savemat
    from python.loaders.arrays import array_page
    p = tmp_path / "s.mat"
    savemat(str(p), {"s": sp.csr_matrix(np.array([[1.0, 0.0], [0.0, 2.0]]))})
    loaded = load_hier(str(p))
    arr = node_arr(loaded, "/s")
    assert arr.shape == (2, 2) and arr[1, 1] == 2.0
    json.dumps(array_page(arr))  # must not raise
