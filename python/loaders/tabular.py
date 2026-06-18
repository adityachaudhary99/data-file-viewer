from dataclasses import dataclass
import pandas as pd
import pyarrow.parquet as pq


@dataclass
class LoadedTable:
    df: pd.DataFrame
    sampled: bool
    total: int


def load_tabular(path: str, max_rows: int = 200_000) -> LoadedTable:
    total = pq.ParquetFile(path).metadata.num_rows
    df = pd.read_parquet(path)
    sampled = total > max_rows
    if sampled:
        df = df.head(max_rows)
    return LoadedTable(df=df, sampled=sampled, total=total)


def columns_meta(df: pd.DataFrame) -> list:
    return [{"name": str(c), "dtype": str(df[c].dtype)} for c in df.columns]
