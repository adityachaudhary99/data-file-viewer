import os
from python.loaders.tabular import load_tabular
from python.paging import page

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample.parquet")


def _df():
    return load_tabular(FIXTURE).df


def test_page_slices_offset_limit():
    res = page(_df(), offset=0, limit=3, sort_by=None, sort_dir=None)
    assert res["total"] == 10
    assert len(res["rows"]) == 3
    assert res["rows"][0][0] == 0  # id column, first row


def test_page_sort_desc_by_id():
    res = page(_df(), offset=0, limit=2, sort_by="id", sort_dir="desc")
    assert res["rows"][0][0] == 9
    assert res["rows"][1][0] == 8


def test_page_nan_becomes_null():
    # price has NaN at row id=3; pull that row
    res = page(_df(), offset=3, limit=1, sort_by="id", sort_dir="asc")
    assert res["rows"][0][1] is None  # price cell is JSON null, not NaN
