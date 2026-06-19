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
