import pandas as pd
from python.jsonsafe import to_jsonable, as_hashable


def page(df, offset: int, limit: int, sort_by, sort_dir) -> dict:
    """Return one page of a DataFrame view as JSON-safe rows.

    `total` is the row count of the passed-in DataFrame (the loaded view).
    When the loader capped a large file, callers surface the true file size
    separately via LoadedTable.total — this function does not re-read the file.
    """
    total = len(df)
    view = df
    if sort_by is not None and sort_by in df.columns:
        view = df.sort_values(by=sort_by, ascending=(sort_dir != "desc"),
                              kind="mergesort", key=as_hashable)
    window = view.iloc[offset: offset + limit]
    rows = [[to_jsonable(v) for v in row] for row in window.itertuples(index=False, name=None)]
    out = {"rows": rows, "total": total, "offset": int(offset)}
    if pd.api.types.is_integer_dtype(window.index):
        out["index"] = window.index.tolist()  # original row numbers, also after sorting
    return out
