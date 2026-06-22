import os
from python.loaders.objects import load_auto
from python.loaders.tabular import columns_meta

BASE = os.path.join(os.path.dirname(__file__), "fixtures")

def test_dataframe_pickle_is_tabular():
    a = load_auto(os.path.join(BASE, "sample_df.pkl"))
    assert a.kind == "tabular"
    assert [c["name"] for c in columns_meta(a.table.df)] == ["id", "price", "region", "active"]
    assert a.table.total == 10

def test_dataframe_joblib_is_tabular():
    a = load_auto(os.path.join(BASE, "sample_df.joblib"))
    assert a.kind == "tabular" and a.table.total == 10

def test_record_list_msgpack_is_tabular():
    a = load_auto(os.path.join(BASE, "sample_records.msgpack"))
    assert a.kind == "tabular" and a.table.total == 10

def test_object_pickle_is_object():
    a = load_auto(os.path.join(BASE, "sample_obj.pkl"))
    assert a.kind == "object"
    assert a.obj_json["data"]["model"] == "demo"

def test_object_msgpack_is_object():
    a = load_auto(os.path.join(BASE, "sample_obj.msgpack"))
    assert a.kind == "object"
    assert a.obj_json["data"]["config"]["a"] == 1


def test_empty_list_msgpack_is_tabular(tmp_path):
    import msgpack
    p = tmp_path / "empty.msgpack"
    p.write_bytes(msgpack.packb([]))
    a = load_auto(str(p))
    assert a.kind == "tabular" and a.table.total == 0
