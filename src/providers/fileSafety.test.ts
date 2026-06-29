import { test } from 'node:test';
import assert from 'node:assert/strict';
import { requiresTrustWarning } from './fileSafety';

test('pickle and joblib extensions require trust warning', () => {
  for (const ext of ['.pkl', '.pickle', '.joblib', '.jl']) {
    assert.equal(requiresTrustWarning(ext), true);
  }
});

test('non-code data extensions do not require trust warning', () => {
  for (const ext of ['.parquet', '.npy', '.npz', '.h5', '.msgpack']) {
    assert.equal(requiresTrustWarning(ext), false);
  }
});
