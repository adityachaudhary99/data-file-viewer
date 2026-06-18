// src/backend/DataSession.test.ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'child_process';
import * as path from 'path';
import { DataSession } from './DataSession';

function fakeSession() {
  const script = path.join(__dirname, '__fixtures__', 'echo-session.cjs');
  return DataSession.fromChild(spawn(process.execPath, [script], { stdio: 'pipe' }));
}

test('open() returns metadata from the session', async () => {
  const s = fakeSession();
  const meta = await s.open();
  assert.equal(meta.shapeKind, 'tabular');
  assert.equal(meta.rowCount, 1);
  s.dispose();
});

test('page() returns rows', async () => {
  const s = fakeSession();
  const res = await s.page({ offset: 0, limit: 10 });
  assert.deepEqual(res.rows, [[0]]);
  s.dispose();
});

test('in-flight request rejects when child exits', async () => {
  const script = path.join(__dirname, '__fixtures__', 'echo-session.cjs');
  const child = spawn(process.execPath, [script], { stdio: 'pipe' });
  const s = DataSession.fromChild(child);
  // Queue an in-flight request, then kill child before the event loop can deliver a reply.
  // The echo-session replies synchronously on its end, but Node delivers data events
  // asynchronously. Killing via SIGKILL before yielding ensures the child exits before
  // the reply reaches us, so rpc.dispose() (wired to child 'exit') rejects the pending req.
  const inFlight = s.profile('will-not-reply');
  child.kill('SIGKILL');
  // The child-exit wiring (child.on('exit', () => rpc.dispose())) rejects in-flight requests
  await assert.rejects(inFlight, /disposed/);
});
