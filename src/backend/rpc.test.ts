// src/backend/rpc.test.ts
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PassThrough } from 'stream';
import { JsonLineRpc } from './rpc';

function harness() {
  const toServer = new PassThrough();   // rpc writes here
  const fromServer = new PassThrough(); // rpc reads here
  const rpc = new JsonLineRpc(toServer, fromServer);
  return { toServer, fromServer, rpc };
}

test('request resolves with matching reply result', async () => {
  const { toServer, fromServer, rpc } = harness();
  const p = rpc.request('open');
  // read what rpc wrote, assert it carries id 1
  const written = JSON.parse((await once(toServer)).toString());
  assert.equal(written.id, 1);
  assert.equal(written.cmd, 'open');
  fromServer.write(JSON.stringify({ id: 1, ok: true, result: { shapeKind: 'tabular' } }) + '\n');
  assert.deepEqual(await p, { shapeKind: 'tabular' });
});

test('request rejects on ok:false', async () => {
  const { fromServer, rpc, toServer } = harness();
  const p = rpc.request('page');
  await once(toServer);
  fromServer.write(JSON.stringify({ id: 1, ok: false, error: 'boom' }) + '\n');
  await assert.rejects(p, /boom/);
});

test('handles two replies arriving in one chunk, out of order', async () => {
  const { fromServer, rpc, toServer } = harness();
  const p1 = rpc.request('a'); await once(toServer);
  const p2 = rpc.request('b'); await once(toServer);
  fromServer.write(
    JSON.stringify({ id: 2, ok: true, result: 'B' }) + '\n' +
    JSON.stringify({ id: 1, ok: true, result: 'A' }) + '\n');
  assert.equal(await p1, 'A');
  assert.equal(await p2, 'B');
});

test('args cannot override protocol id field', async () => {
  const { toServer, rpc } = harness();
  // Caller supplies id:999 in args — protocol id must still be the real incrementing id (1).
  const _p = rpc.request('x', { id: 999 });
  const written = JSON.parse((await once(toServer)).toString());
  assert.equal(written.id, 1, 'protocol id must be the real incrementing id, not the arg override');
  assert.equal(written.cmd, 'x');
});

function once(stream: PassThrough): Promise<Buffer> {
  return new Promise((res) => stream.once('data', res));
}
