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
