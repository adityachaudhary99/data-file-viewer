import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.classify import classify
from python.loaders.tabular import load_tabular, columns_meta
from python.loaders.objects import load_auto
from python.loaders.arrays import load_arrays, member_meta, array_page, array_profile, array_raw
from python.loaders.hierarchical import load_hier, node_arr, hier_raw
from python.paging import page as page_df
from python.profiler import profile_column
from python.jsonsafe import to_jsonable

MAX_ROWS = 200_000
RAW_LIMIT = 1000


class Session:
    def __init__(self, path: str):
        self.path = path
        self.kind = classify(path)          # "tabular" | "array" | "hierarchical" | "auto"
        self._table = None
        self._obj_json = None
        self._arrays = None
        self._hier = None
        self.shape_kind = None              # "tabular" | "object" | "array" | "hierarchical"

    def _ensure_loaded(self):
        if self.shape_kind is not None:
            return
        if self.kind == "tabular":
            self._table = load_tabular(self.path, MAX_ROWS)
            self.shape_kind = "tabular"
        elif self.kind == "array":
            self._arrays = load_arrays(self.path)
            self.shape_kind = "array"
        elif self.kind == "hierarchical":
            self._hier = load_hier(self.path)
            self.shape_kind = "hierarchical"
        else:  # auto
            a = load_auto(self.path, MAX_ROWS)
            self.shape_kind = a.kind
            self._table = a.table
            self._obj_json = a.obj_json

    def _member_arr(self, name):
        members = self._arrays.members
        for m in members:
            if m.name == name:
                return m.arr
        if not members:
            raise ValueError("archive has no arrays")
        return members[0].arr

    def _node_arr(self, name):
        arr = node_arr(self._hier, name)
        if arr is None:
            raise ValueError("file has no displayable dataset")
        return arr

    def handle(self, req: dict) -> dict:
        cmd = req.get("cmd")
        if cmd == "open":
            self._ensure_loaded()
            if self.shape_kind == "object":
                return {"shapeKind": "object", "fileMeta": {"name": os.path.basename(self.path)}}
            if self.shape_kind == "array":
                return {"shapeKind": "array",
                        "members": [dict(name=m.name, **member_meta(m.arr)) for m in self._arrays.members],
                        "fileMeta": {"name": os.path.basename(self.path)}}
            if self.shape_kind == "hierarchical":
                return {"shapeKind": "hierarchical",
                        "tree": self._hier.nodes,
                        "fileMeta": {"name": os.path.basename(self.path)}}
            t = self._table
            return {"shapeKind": "tabular", "columns": columns_meta(t.df),
                    "rowCount": t.total, "sampled": t.sampled}
        self._ensure_loaded()
        if self.shape_kind == "object":
            if cmd == "rawJson":
                return {"json": self._obj_json}
            raise ValueError(f"command {cmd!r} not available for object files")
        if self.shape_kind == "array":
            # member name rides on the `column` request field (no RPC change)
            if cmd == "page":
                return array_page(self._member_arr(req.get("column")),
                                  req.get("offset", 0), req.get("limit", 200))
            if cmd == "profile":
                return array_profile(self._member_arr(req.get("column")))
            if cmd == "rawJson":
                return {"json": array_raw(self._arrays, self.path)}
            raise ValueError(f"command {cmd!r} not available for array files")
        if self.shape_kind == "hierarchical":
            # node path rides on the `column` request field (no RPC change)
            if cmd == "page":
                return array_page(self._node_arr(req.get("column")),
                                  req.get("offset", 0), req.get("limit", 200))
            if cmd == "profile":
                return array_profile(self._node_arr(req.get("column")))
            if cmd == "rawJson":
                return {"json": hier_raw(self._hier, self.path)}
            raise ValueError(f"command {cmd!r} not available for hierarchical files")
        # tabular commands (unchanged)
        if cmd == "page":
            return page_df(self._table.df, req.get("offset", 0), req.get("limit", 200),
                           req.get("sortBy"), req.get("sortDir"))
        if cmd == "profile":
            return profile_column(self._table.df[req["column"]])
        if cmd == "rawJson":
            df = self._table.df.head(RAW_LIMIT)
            data = [{k: to_jsonable(v) for k, v in rec.items()}
                    for rec in df.to_dict(orient="records")]
            return {"json": {"file_type": os.path.splitext(self.path)[1].lstrip("."),
                             "rows": self._table.total,
                             "shown": len(data),
                             "truncated": self._table.total > len(data),
                             "columns": [str(c) for c in self._table.df.columns],
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
