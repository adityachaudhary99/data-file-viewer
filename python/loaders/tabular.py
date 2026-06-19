import os
from dataclasses import dataclass
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.ipc


@dataclass
class LoadedTable:
    df: pd.DataFrame
    sampled: bool
    total: int


def _read_arrow_ipc(path: str) -> pd.DataFrame:
    with pa.memory_map(path, "r") as source:
        try:
            table = pa.ipc.open_file(source).read_all()
        except pa.lib.ArrowInvalid:
            source.seek(0)
            table = pa.ipc.open_stream(source).read_all()
    return table.to_pandas()


def _read_avro(path: str) -> pd.DataFrame:
    from avro.datafile import DataFileReader
    from avro.io import DatumReader
    with open(path, "rb") as f:
        reader = DataFileReader(f, DatumReader())
        records = list(reader)
        reader.close()
    return pd.DataFrame.from_records(records)


def _read_table(path: str):
    """Return (full_dataframe, true_row_count) for a supported tabular file."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".parquet":
        total = pq.ParquetFile(path).metadata.num_rows
        return pd.read_parquet(path), total
    if ext == ".feather":
        df = pd.read_feather(path)
        return df, len(df)
    if ext == ".arrow":
        df = _read_arrow_ipc(path)
        return df, len(df)
    if ext == ".avro":
        df = _read_avro(path)
        return df, len(df)
    raise ValueError(f"unsupported tabular extension: {ext}")


def load_tabular(path: str, max_rows: int = 200_000) -> LoadedTable:
    df, total = _read_table(path)
    sampled = total > max_rows
    if sampled:
        df = df.head(max_rows)
    return LoadedTable(df=df, sampled=sampled, total=total)


def columns_meta(df: pd.DataFrame) -> list:
    return [{"name": str(c), "dtype": str(df[c].dtype)} for c in df.columns]
