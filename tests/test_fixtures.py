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


def test_feather_and_arrow_fixtures_match_parquet_shape():
    import pandas as pd
    base = os.path.join(os.path.dirname(__file__), "fixtures")
    feather_df = pd.read_feather(os.path.join(base, "sample.feather"))
    assert list(feather_df.columns) == ["id", "price", "region", "active"]
    assert len(feather_df) == 10
    assert feather_df["price"].isna().sum() == 1
    import pyarrow as pa
    with pa.memory_map(os.path.join(base, "sample.arrow"), "r") as src:
        arrow_df = pa.ipc.open_file(src).read_all().to_pandas()
    assert list(arrow_df.columns) == ["id", "price", "region", "active"]
    assert len(arrow_df) == 10


def test_plan3_fixtures_exist():
    base = os.path.join(os.path.dirname(__file__), "fixtures")
    for name in ["sample.avro", "sample_df.pkl", "sample_df.joblib",
                 "sample_obj.pkl", "sample_records.msgpack", "sample_obj.msgpack"]:
        p = os.path.join(base, name)
        assert os.path.exists(p) and os.path.getsize(p) > 0, name
