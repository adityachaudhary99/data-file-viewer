import os
import numpy as np
from python.loaders.hierarchical import load_hier, node_arr

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
