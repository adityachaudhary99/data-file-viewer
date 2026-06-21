export function scaleHistogram(counts: number[], maxPx: number): number[] {
  const max = Math.max(0, ...counts);
  if (max === 0) return counts.map(() => 0);
  return counts.map((c) => Math.round((c / max) * maxPx));
}

export function formatStat(v: number | null): string {
  if (v === null || v === undefined || Number.isNaN(v)) return '—';
  if (Number.isInteger(v)) return String(v);
  return Number(v.toPrecision(4)).toString();
}

function csvField(value: unknown): string {
  if (value === null || value === undefined) return '';
  const s = String(value);
  return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

export function rowsToCsv(columns: string[], rows: unknown[][]): string {
  const lines = [columns.map(csvField).join(',')];
  for (const row of rows) lines.push(row.map(csvField).join(','));
  return lines.join('\r\n');
}

export function formatShape(shape: number[]): string {
  if (!shape || shape.length === 0) return '()';
  return shape.join(' × ');
}

export function treeIndent(depth: number): number {
  return 6 + depth * 12;
}

export function csvFileName(name: string): string {
  const dot = name.lastIndexOf('.');
  return (dot > 0 ? name.slice(0, dot) : name) + '.csv';
}
