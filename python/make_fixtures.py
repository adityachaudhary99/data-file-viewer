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


def make_array_fixtures(fixture_dir: str) -> None:
    import numpy as np
    a2d = np.arange(12, dtype="float64").reshape(4, 3)
    a2d[1, 1] = np.nan
    a2d[2, 0] = np.inf
    np.save(os.path.join(fixture_dir, "arr_2d.npy"), a2d)
    np.save(os.path.join(fixture_dir, "arr_1d.npy"), np.arange(10, dtype="int64"))
    np.save(os.path.join(fixture_dir, "arr_3d.npy"), np.arange(24, dtype="float64").reshape(2, 3, 4))
    np.save(os.path.join(fixture_dir, "arr_scalar.npy"), np.array(42.0))
    np.save(os.path.join(fixture_dir, "arr_str.npy"), np.array(["alpha", "beta", "gamma"]))
    np.savez(os.path.join(fixture_dir, "sample.npz"),
             x=np.arange(6, dtype="int64"), y=np.arange(6, dtype="float64").reshape(3, 2))
    print("wrote npy/npz array fixtures")


def make_hier_fixtures(fixture_dir: str) -> None:
    import numpy as np
    import h5py
    from netCDF4 import Dataset
    from scipy.io import savemat

    # --- HDF5: root datasets + one group with a NaN-bearing 2-D dataset ---
    with h5py.File(os.path.join(fixture_dir, "sample.h5"), "w") as f:
        f.create_dataset("ids", data=np.arange(5, dtype="int64"))
        f.create_dataset("labels", data=np.array([b"alpha", b"beta", b"gamma"]))
        grp = f.create_group("grp")
        vals = np.arange(12, dtype="float64").reshape(3, 4)
        vals[0, 0] = np.nan
        grp.create_dataset("values", data=vals)

    # --- NetCDF4: two root variables + one nested group with a variable ---
    nc = Dataset(os.path.join(fixture_dir, "sample.nc"), "w", format="NETCDF4")
    nc.createDimension("t", 4)
    nc.createVariable("temp", "f8", ("t",))[:] = np.array([10.0, 11.5, 9.0, 12.0])
    nc.createVariable("pressure", "f8", ("t",))[:] = np.array([101.0, 100.5, 102.0, 99.5])
    region = nc.createGroup("region")
    region.createDimension("r", 3)
    region.createVariable("rid", "i4", ("r",))[:] = np.array([1, 2, 3])
    nc.close()

    # --- MATLAB v5: two arrays + one struct (-> group) with numeric fields ---
    savemat(os.path.join(fixture_dir, "sample.mat"), {
        "matrix": np.arange(6, dtype="float64").reshape(2, 3),
        "vector": np.arange(4, dtype="int32"),
        "params": {"a": np.float64(3.5), "b": np.arange(3, dtype="float64")},
    })
    print("wrote h5/nc/mat hierarchical fixtures")


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

    make_array_fixtures(FIXTURE_DIR)
    make_hier_fixtures(FIXTURE_DIR)


if __name__ == "__main__":
    main()
