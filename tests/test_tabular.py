import os
from python.loaders.tabular import load_tabular, columns_meta

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample.parquet")


def test_load_tabular_returns_full_table_when_under_cap():
    t = load_tabular(FIXTURE, max_rows=200_000)
    assert t.total == 10
    assert t.sampled is False
    assert len(t.df) == 10


def test_load_tabular_caps_and_flags_sampled():
    t = load_tabular(FIXTURE, max_rows=5)
    assert t.total == 10
    assert t.sampled is True
    assert len(t.df) == 5


def test_columns_meta_shape():
    t = load_tabular(FIXTURE)
    meta = columns_meta(t.df)
    assert {"name": "id", "dtype": meta[0]["dtype"]} == meta[0]
    assert [c["name"] for c in meta] == ["id", "price", "region", "active"]
