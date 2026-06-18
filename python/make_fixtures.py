# python/make_fixtures.py
"""Generate small, deterministic test fixtures. Run: python python/make_fixtures.py"""
import os
import pandas as pd

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")


def make_sample_dataframe() -> pd.DataFrame:
    price = [1.0, 2.5, 3.0, float("nan"), 5.5, 6.0, 7.25, 8.0, 9.5, 10.0]
    region = ["north", "north", "north", "north", "north", "north",
              "south", "south", "south", "east"]
    return pd.DataFrame({
        "id": list(range(10)),
        "price": price,
        "region": region,
        "active": [True, False] * 5,
    })


def main() -> None:
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    df = make_sample_dataframe()
    df.to_parquet(os.path.join(FIXTURE_DIR, "sample.parquet"), index=False)
    print("wrote sample.parquet")

    import pyarrow as pa
    import pyarrow.feather as feather
    import pyarrow.ipc as ipc

    table = pa.Table.from_pandas(df, preserve_index=False)
    feather.write_feather(table, os.path.join(FIXTURE_DIR, "sample.feather"))
    with pa.OSFile(os.path.join(FIXTURE_DIR, "sample.arrow"), "wb") as sink:
        with ipc.new_file(sink, table.schema) as writer:
            writer.write_table(table)
    print("wrote sample.feather and sample.arrow")


if __name__ == "__main__":
    main()
