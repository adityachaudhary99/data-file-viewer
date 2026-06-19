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

    import pickle, json as _json
    import joblib
    import msgpack

    # tabular pickles / joblib
    df.to_pickle(os.path.join(FIXTURE_DIR, "sample_df.pkl"))
    joblib.dump(df, os.path.join(FIXTURE_DIR, "sample_df.joblib"))

    # non-tabular (object) pickle
    with open(os.path.join(FIXTURE_DIR, "sample_obj.pkl"), "wb") as f:
        pickle.dump({"model": "demo", "params": {"depth": 6, "lr": 0.1}, "weights": [1, 2, 3]}, f)

    # record-list msgpack (tabular) — price NaN -> None for clean records
    records = [
        {k: (None if (isinstance(v, float) and v != v) else v) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]
    with open(os.path.join(FIXTURE_DIR, "sample_records.msgpack"), "wb") as f:
        f.write(msgpack.packb(records))
    # object msgpack
    with open(os.path.join(FIXTURE_DIR, "sample_obj.msgpack"), "wb") as f:
        f.write(msgpack.packb({"config": {"a": 1, "b": [1, 2, 3]}}))

    # avro (records; price as nullable double)
    import avro.schema
    from avro.datafile import DataFileWriter
    from avro.io import DatumWriter
    schema = avro.schema.parse(_json.dumps({
        "type": "record", "name": "Row", "fields": [
            {"name": "id", "type": "int"},
            {"name": "price", "type": ["null", "double"]},
            {"name": "region", "type": "string"},
            {"name": "active", "type": "boolean"},
        ],
    }))
    with open(os.path.join(FIXTURE_DIR, "sample.avro"), "wb") as f:
        writer = DataFileWriter(f, DatumWriter(), schema)
        for row in df.to_dict(orient="records"):
            writer.append({
                "id": int(row["id"]),
                "price": (None if row["price"] != row["price"] else float(row["price"])),
                "region": str(row["region"]),
                "active": bool(row["active"]),
            })
        writer.close()
    print("wrote avro + pickle/joblib/msgpack fixtures")


if __name__ == "__main__":
    main()
