import os
import pandas as pd
from python.loaders.tabular import load_tabular
from python.profiler import profile_column, histogram

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample.parquet")


def _df():
    return load_tabular(FIXTURE).df


def test_numeric_profile_price():
    p = profile_column(_df()["price"])
    assert p["kind"] == "numeric"
    assert p["nulls"] == 1
    assert round(p["nullPct"], 2) == 0.10
    assert p["min"] == 1.0 and p["max"] == 10.0
    assert len(p["histogram"]["counts"]) == 20


def test_categorical_profile_region():
    p = profile_column(_df()["region"])
    assert p["kind"] == "categorical"
    assert p["top"][0] == {"value": "north", "count": 6}


def test_boolean_profile_active():
    p = profile_column(_df()["active"])
    assert p["kind"] == "boolean"
    assert p["trueCount"] == 5 and p["falseCount"] == 5


def test_flags_constant_column():
    p = profile_column(pd.Series([7, 7, 7], name="c"))
    assert p["flags"]["constant"] is True


def test_histogram_counts_sum_to_non_null_count():
    s = _df()["price"]
    h = histogram(s)
    assert sum(h["counts"]) == int(s.notna().sum())


def test_histogram_empty_when_no_numeric_values():
    h = histogram(pd.Series([None, None, None]))
    assert h == {"edges": [], "counts": []}


import json

def test_profile_complex_column():
    import json
    p = profile_column(pd.Series([1+2j, 3+4j]))
    assert p["kind"] == "categorical"
    json.dumps(p)  # must not raise
