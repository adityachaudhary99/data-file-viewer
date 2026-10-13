import json
import os
import numpy as np
import pyarrow as pa
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


def _list_df():
    values = pa.array(np.array([3, 4, 5, 0, 1, 2, 6, 7, 8], dtype=np.float32))
    return pa.table({"pos": pa.FixedSizeListArray.from_arrays(values, 3)}).to_pandas()


def test_page_list_column_rows_are_json_lists():
    res = page(_list_df(), offset=0, limit=3, sort_by=None, sort_dir=None)
    assert res["rows"][0] == [[3.0, 4.0, 5.0]]
    assert json.dumps(res)  # must not raise


def test_page_sort_by_list_column():
    res = page(_list_df(), offset=0, limit=3, sort_by="pos", sort_dir="desc")
    assert [r[0][0] for r in res["rows"]] == [6.0, 3.0, 0.0]


def test_page_reports_offset_and_original_row_numbers():
    res = page(_df(), offset=4, limit=3, sort_by=None, sort_dir=None)
    assert res["offset"] == 4 and res["index"] == [4, 5, 6]
    res = page(_df(), offset=0, limit=2, sort_by="id", sort_dir="desc")
    assert res["index"] == [9, 8]  # positions in the file, not in the sorted view
