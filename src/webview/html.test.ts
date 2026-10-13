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

test('every element id the webview script looks up exists in the markup', () => {
  const html = getExplorerHtml({ fileName: 'sample.parquet', cspSource: 'vscode-resource:', nonce: 'test-nonce' });
  const script = html.match(/<script nonce="test-nonce">([\s\S]*)<\/script>/)?.[1] ?? '';
  const markup = html.replace(script, '');
  const ids = new Set([...script.matchAll(/\$\('([\w-]+)'\)/g)].map((m) => m[1]));
  assert.ok(ids.has('pgNext') && ids.has('tableWrap'));
  const missing = [...ids].filter((id) => !markup.includes(`id="${id}"`));
  assert.deepEqual(missing, []);
});
