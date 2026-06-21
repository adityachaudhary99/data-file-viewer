import os
import sys
import json
import subprocess

ROOT = os.path.dirname(os.path.dirname(__file__))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "sample.parquet")
SESSION = os.path.join(ROOT, "python", "session.py")


def _run(requests):
    proc = subprocess.run(
        [sys.executable, SESSION, FIXTURE],
        input="\n".join(json.dumps(r) for r in requests) + "\n",
        capture_output=True, text=True, cwd=ROOT, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]


def test_open_returns_tabular_metadata():
    [reply] = _run([{"id": 1, "cmd": "open"}])
    assert reply["id"] == 1 and reply["ok"] is True
    r = reply["result"]
    assert r["shapeKind"] == "tabular"
    assert [c["name"] for c in r["columns"]] == ["id", "price", "region", "active"]
    assert r["rowCount"] == 10 and r["sampled"] is False


def test_page_and_profile_roundtrip():
    replies = _run([
        {"id": 1, "cmd": "page", "offset": 0, "limit": 2, "sortBy": "id", "sortDir": "desc"},
        {"id": 2, "cmd": "profile", "column": "region"},
    ])
    by_id = {r["id"]: r for r in replies}
    assert by_id[1]["result"]["rows"][0][0] == 9
    assert by_id[2]["result"]["kind"] == "categorical"


def test_unknown_command_returns_error_not_crash():
    [reply] = _run([{"id": 7, "cmd": "nope"}])
    assert reply["id"] == 7 and reply["ok"] is False
    assert "nope" in reply["error"]


def test_malformed_json_line_does_not_crash():
    proc = subprocess.run(
        [sys.executable, SESSION, FIXTURE],
        input='{bad json}\n' + json.dumps({"id": 5, "cmd": "open"}) + "\n",
        capture_output=True, text=True, cwd=ROOT, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    replies = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
    by_id = {r.get("id"): r for r in replies}
    assert by_id[5]["ok"] is True  # valid request after the bad line still works


def test_rawjson_reports_truncation_keys():
    [reply] = _run([{"id": 1, "cmd": "rawJson"}])
    j = reply["result"]["json"]
    assert j["shown"] == 10
    assert j["truncated"] is False
    assert len(j["data"]) == 10


def _run_on(fixture, requests):
    path = os.path.join(ROOT, "tests", "fixtures", fixture)
    proc = subprocess.run(
        [sys.executable, SESSION, path],
        input="\n".join(json.dumps(r) for r in requests) + "\n",
        capture_output=True, text=True, cwd=ROOT, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    return [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]


def test_open_tabular_pickle():
    [r] = _run_on("sample_df.pkl", [{"id": 1, "cmd": "open"}])
    assert r["result"]["shapeKind"] == "tabular"
    assert r["result"]["rowCount"] == 10


def test_open_object_pickle_then_rawjson():
    rs = _run_on("sample_obj.pkl", [{"id": 1, "cmd": "open"}, {"id": 2, "cmd": "rawJson"}])
    by = {r["id"]: r for r in rs}
    assert by[1]["result"]["shapeKind"] == "object"
    assert by[2]["result"]["json"]["data"]["model"] == "demo"


def test_avro_opens_tabular():
    [r] = _run_on("sample.avro", [{"id": 1, "cmd": "open"}])
    assert r["result"]["shapeKind"] == "tabular" and r["result"]["rowCount"] == 10


def test_open_npy_is_array_with_one_member():
    [r] = _run_on("arr_2d.npy", [{"id": 1, "cmd": "open"}])
    res = r["result"]
    assert res["shapeKind"] == "array"
    assert [m["name"] for m in res["members"]] == ["array"]
    assert res["members"][0]["shape"] == [4, 3]


def test_open_npz_lists_members():
    [r] = _run_on("sample.npz", [{"id": 1, "cmd": "open"}])
    assert [m["name"] for m in r["result"]["members"]] == ["x", "y"]


def test_array_page_and_profile_select_member_via_column():
    rs = _run_on("sample.npz", [
        {"id": 1, "cmd": "page", "column": "y", "offset": 0, "limit": 100},
        {"id": 2, "cmd": "profile", "column": "y"},
    ])
    by = {r["id"]: r for r in rs}
    assert by[1]["result"]["rowCount"] == 3 and by[1]["result"]["colCount"] == 2
    assert by[2]["result"]["kind"] == "numeric"


def test_array_page_defaults_to_first_member():
    [r] = _run_on("sample.npz", [{"id": 1, "cmd": "page", "offset": 0, "limit": 100}])
    assert r["result"]["rowCount"] == 6 and r["result"]["colCount"] == 1  # member x (1-D)


def test_array_rawjson_summary():
    [r] = _run_on("arr_1d.npy", [{"id": 1, "cmd": "rawJson"}])
    j = r["result"]["json"]
    assert j["file_type"] == "npy"
    assert j["members"][0]["preview"] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_open_h5_is_hierarchical_tree():
    [r] = _run_on("sample.h5", [{"id": 1, "cmd": "open"}])
    res = r["result"]
    assert res["shapeKind"] == "hierarchical"
    paths = [(n["path"], n["kind"]) for n in res["tree"]]
    assert paths == [("/grp", "group"), ("/grp/values", "leaf"),
                     ("/ids", "leaf"), ("/labels", "leaf")]


def test_h5_page_and_profile_select_node_via_column():
    rs = _run_on("sample.h5", [
        {"id": 1, "cmd": "page", "column": "/grp/values", "offset": 0, "limit": 100},
        {"id": 2, "cmd": "profile", "column": "/ids"},
    ])
    by = {r["id"]: r for r in rs}
    assert by[1]["result"]["rowCount"] == 3 and by[1]["result"]["colCount"] == 4
    assert by[2]["result"]["kind"] == "numeric" and by[2]["result"]["max"] == 4


def test_nc_open_and_mat_open_are_hierarchical():
    [a] = _run_on("sample.nc", [{"id": 1, "cmd": "open"}])
    assert a["result"]["shapeKind"] == "hierarchical"
    assert any(n["path"] == "/region/rid" for n in a["result"]["tree"])
    [b] = _run_on("sample.mat", [{"id": 1, "cmd": "open"}])
    assert b["result"]["shapeKind"] == "hierarchical"
    assert any(n["path"] == "/params" and n["kind"] == "group" for n in b["result"]["tree"])


def test_h5_rawjson_summary():
    [r] = _run_on("sample.h5", [{"id": 1, "cmd": "rawJson"}])
    j = r["result"]["json"]
    assert j["file_type"] == "h5"
    by = {n["path"]: n for n in j["nodes"]}
    assert by["/ids"]["preview"] == [0, 1, 2, 3, 4]
