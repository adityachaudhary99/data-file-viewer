import { test } from 'node:test';
import assert from 'node:assert/strict';
import { scaleHistogram, formatStat, rowsToCsv, formatShape, treeIndent, csvFileName } from './viewmodel';

test('scaleHistogram scales tallest bar to maxPx', () => {
  assert.deepEqual(scaleHistogram([0, 5, 10], 100), [0, 50, 100]);
});
test('scaleHistogram all-zero is safe', () => {
  assert.deepEqual(scaleHistogram([0, 0], 100), [0, 0]);
});
test('formatStat handles null and floats', () => {
  assert.equal(formatStat(null), '—');
  assert.equal(formatStat(3), '3');
  assert.equal(formatStat(3.14159), '3.142');
});
test('rowsToCsv quotes and escapes', () => {
  const csv = rowsToCsv(['a', 'b'], [['x,y', null], ['he said "hi"', 2]]);
  assert.equal(csv, 'a,b\r\n"x,y",\r\n"he said ""hi""",2');
});

test('formatShape joins dims and renders scalar', () => {
  assert.strictEqual(formatShape([4, 3]), '4 × 3');
  assert.strictEqual(formatShape([10]), '10');
  assert.strictEqual(formatShape([]), '()');
});

test('treeIndent grows with depth', () => {
  assert.strictEqual(treeIndent(0), 6);
  assert.strictEqual(treeIndent(2), 30);
});

test('csvFileName swaps the extension for .csv', () => {
  assert.strictEqual(csvFileName('sample.parquet'), 'sample.csv');
  assert.strictEqual(csvFileName('a.b.h5'), 'a.b.csv');
  assert.strictEqual(csvFileName('noext'), 'noext.csv');
});

test('formatStat returns em-dash for null, undefined, NaN', () => {
  assert.equal(formatStat(null), '—');
  assert.equal(formatStat(undefined as unknown as number), '—');
  assert.equal(formatStat(NaN), '—');
});
test('formatStat returns string for non-number input', () => {
  assert.equal(formatStat('abc' as unknown as number), 'abc');
});
test('formatStat formats integers and 4-sig-fig floats', () => {
  assert.equal(formatStat(5), '5');
  assert.equal(formatStat(3.14159), '3.142');
});
