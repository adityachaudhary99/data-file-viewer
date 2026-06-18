// src/backend/__fixtures__/echo-session.cjs
// Minimal NDJSON server: replies to open/page/profile deterministically.
// Special command "exit" causes the process to exit after sending a reply,
// so tests can verify in-flight requests reject on child exit.
let buf = '';
process.stdin.on('data', (c) => {
  buf += c.toString();
  let nl;
  while ((nl = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, nl).trim();
    buf = buf.slice(nl + 1);
    if (!line) continue;
    const req = JSON.parse(line);
    let result;
    if (req.cmd === 'open') result = { shapeKind: 'tabular', columns: [{ name: 'id', dtype: 'int64' }], rowCount: 1, sampled: false };
    else if (req.cmd === 'page') result = { rows: [[0]], total: 1 };
    else result = { echo: req.cmd };
    process.stdout.write(JSON.stringify({ id: req.id, ok: true, result }) + '\n');
    if (req.cmd === 'exit') process.exit(0);
  }
});
