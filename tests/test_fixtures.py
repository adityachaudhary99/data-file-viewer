# tests/test_fixtures.py
import os
import pandas as pd

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample.parquet")


def test_sample_fixture_exists_and_has_expected_shape():
    assert os.path.exists(FIXTURE), "run: python python/make_fixtures.py"
    df = pd.read_parquet(FIXTURE)
    assert list(df.columns) == ["id", "price", "region", "active"]
    assert len(df) == 10
    assert df["price"].isna().sum() == 1
    assert pd.isna(df.loc[3, "price"])
    assert pd.api.types.is_integer_dtype(df["id"])
    assert pd.api.types.is_float_dtype(df["price"])
    assert pd.api.types.is_bool_dtype(df["active"])
