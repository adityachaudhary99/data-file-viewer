import { test } from 'node:test';
import assert from 'node:assert/strict';
import { getExplorerHtml } from './html';

test('generated webview script parses as JavaScript', () => {
  const html = getExplorerHtml({
    fileName: 'sample.parquet',
    cspSource: 'vscode-resource:',
    nonce: 'test-nonce',
  });

  const script = html.match(/<script nonce="test-nonce">([\s\S]*)<\/script>/)?.[1];
  assert.ok(script, 'expected inline webview script');
  assert.doesNotThrow(() => new Function(script));
});
