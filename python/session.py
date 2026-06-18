import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.classify import classify
from python.loaders.tabular import load_tabular, columns_meta
from python.paging import page as page_df
from python.profiler import profile_column
from python.jsonsafe import to_jsonable

MAX_ROWS = 200_000
RAW_LIMIT = 1000


class Session:
    def __init__(self, path: str):
        self.path = path
        self.kind = classify(path)
        self._table = None

    @property
    def table(self):
        if self._table is None:
            self._table = load_tabular(self.path, MAX_ROWS)
        return self._table

    def handle(self, req: dict) -> dict:
        cmd = req.get("cmd")
        if cmd == "open":
            t = self.table
            return {"shapeKind": self.kind, "columns": columns_meta(t.df),
                    "rowCount": t.total, "sampled": t.sampled}
        if cmd == "page":
            return page_df(self.table.df, req.get("offset", 0), req.get("limit", 100),
                           req.get("sortBy"), req.get("sortDir"))
        if cmd == "profile":
            col = req["column"]
            return profile_column(self.table.df[col])
        if cmd == "rawJson":
            df = self.table.df.head(RAW_LIMIT)
            data = [{k: to_jsonable(v) for k, v in rec.items()}
                    for rec in df.to_dict(orient="records")]
            return {"json": {"file_type": os.path.splitext(self.path)[1].lstrip("."),
                             "rows": self.table.total,
                             "shown": len(data),
                             "truncated": self.table.total > len(data),
                             "columns": [c["name"] for c in columns_meta(self.table.df)],
                             "data": data}}
        raise ValueError(f"unknown command: {cmd!r}")


def main() -> None:
    session = Session(sys.argv[1])
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req = None
        try:
            req = json.loads(line)
            result = session.handle(req)
            reply = {"id": req.get("id"), "ok": True, "result": result}
        except Exception as exc:  # noqa: BLE001 — report, don't crash the session
            rid = req.get("id") if isinstance(req, dict) else None
            reply = {"id": rid, "ok": False, "error": str(exc)}
        sys.stdout.write(json.dumps(reply) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
