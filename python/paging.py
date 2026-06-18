from python.jsonsafe import to_jsonable


def page(df, offset: int, limit: int, sort_by, sort_dir) -> dict:
    total = len(df)
    view = df
    if sort_by is not None and sort_by in df.columns:
        view = df.sort_values(by=sort_by, ascending=(sort_dir != "desc"),
                              kind="mergesort")
    window = view.iloc[offset: offset + limit]
    rows = [[to_jsonable(v) for v in row] for row in window.itertuples(index=False, name=None)]
    return {"rows": rows, "total": total}
