import { test } from 'node:test';
import assert from 'node:assert/strict';
import { scaleHistogram, formatStat, rowsToCsv } from './viewmodel';

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
