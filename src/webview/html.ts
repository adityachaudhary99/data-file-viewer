// src/webview/html.ts
export function getExplorerHtml(opts: { fileName: string; cspSource: string; nonce: string }): string {
  const { fileName, cspSource, nonce } = opts;
  return `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body{margin:0;font-family:var(--vscode-font-family);color:var(--vscode-editor-foreground);background:var(--vscode-editor-background);}
  .tabs{display:flex;gap:4px;padding:6px 10px;border-bottom:1px solid var(--vscode-panel-border);}
  .tab{padding:4px 10px;cursor:pointer;border-radius:4px;}
  .tab.active{background:var(--vscode-button-background);color:var(--vscode-button-foreground);}
  .layout{display:flex;height:calc(100vh - 40px);}
  .nav{width:180px;overflow:auto;border-right:1px solid var(--vscode-panel-border);padding:6px;}
  .nav .col{padding:3px 6px;cursor:pointer;border-radius:3px;}
  .nav .col:hover{background:var(--vscode-list-hoverBackground);}
  .nav .col.sel{background:var(--vscode-list-activeSelectionBackground);}
  .main{flex:1;overflow:auto;padding:6px;}
  .insp{width:240px;border-left:1px solid var(--vscode-panel-border);padding:8px;overflow:auto;}
  table{border-collapse:collapse;width:100%;font-size:12px;}
  th,td{border:1px solid var(--vscode-panel-border);padding:2px 6px;text-align:left;white-space:nowrap;}
  th{position:sticky;top:0;background:var(--vscode-editorGroupHeader-tabsBackground);cursor:pointer;}
  .hist{display:flex;align-items:flex-end;gap:1px;height:60px;}
  .hist i{flex:1;background:var(--vscode-charts-blue,#4e94ce);}
  .hidden{display:none;}
  pre{white-space:pre-wrap;font-family:var(--vscode-editor-font-family);}
  .badge{display:inline-block;font-size:10px;padding:1px 5px;border-radius:3px;background:var(--vscode-inputValidation-warningBackground);margin-right:4px;}
  .note{color:var(--vscode-descriptionForeground);font-size:11px;}
</style></head>
<body>
  <div class="tabs">
    <div class="tab active" data-tab="data">Data</div>
    <div class="tab" data-tab="profile">Profile</div>
    <div class="tab" data-tab="schema">Schema</div>
    <div class="tab" data-tab="raw">Raw</div>
    <span class="note" style="margin-left:auto" id="status">${escapeHtml(fileName)}</span>
  </div>
  <div class="layout">
    <div class="nav" id="nav"></div>
    <div class="main">
      <div id="view-data"><div class="note" id="sampleNote"></div><table id="tbl"></table></div>
      <div id="view-profile" class="hidden"></div>
      <div id="view-schema" class="hidden"></div>
      <div id="view-raw" class="hidden"><pre id="raw"></pre></div>
    </div>
    <div class="insp" id="insp"><div class="note">Select a column</div></div>
  </div>
  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    const fileName = ${JSON.stringify(fileName)};
    let columns = [], sortBy = null, sortDir = null, selected = null;
    const $ = (id) => document.getElementById(id);

    function send(cmd, args) { vscode.postMessage({ type: 'request', cmd, args: args || {} }); }

    function showTab(name) {
      for (const t of document.querySelectorAll('.tab')) t.classList.toggle('active', t.dataset.tab === name);
      for (const v of ['data','profile','schema','raw'])
        $('view-' + v).classList.toggle('hidden', v !== name);
      if (name === 'raw') send('rawJson');
      if (name === 'profile') renderProfileTab();
    }
    document.querySelectorAll('.tab').forEach((t) => t.onclick = () => showTab(t.dataset.tab));

    function renderNav() {
      $('nav').innerHTML = '';
      columns.forEach((c) => {
        const d = document.createElement('div');
        d.className = 'col' + (c.name === selected ? ' sel' : '');
        d.textContent = c.name; d.title = c.dtype;
        d.onclick = () => { selected = c.name; renderNav(); send('profile', { column: c.name }); };
        $('nav').appendChild(d);
      });
    }
    function renderSchema() {
      $('view-schema').innerHTML = '<table><tr><th>column</th><th>dtype</th></tr>' +
        columns.map((c) => '<tr><td>' + esc(c.name) + '</td><td>' + esc(c.dtype) + '</td></tr>').join('') + '</table>';
    }
    function renderTable(rows) {
      const head = '<tr>' + columns.map((c) => '<th data-c="' + esc(c.name) + '">' + esc(c.name) +
        (c.name === sortBy ? (sortDir === 'desc' ? ' ▼' : ' ▲') : '') + '</th>').join('') + '</tr>';
      const body = rows.map((r) => '<tr>' + r.map((v) =>
        '<td>' + (v === null ? '<span class="note">null</span>' : esc(String(v))) + '</td>').join('') + '</tr>').join('');
      $('tbl').innerHTML = head + body;
      $('tbl').querySelectorAll('th').forEach((th) => th.onclick = () => {
        const c = th.dataset.c;
        if (sortBy === c) sortDir = sortDir === 'desc' ? 'asc' : 'desc'; else { sortBy = c; sortDir = 'asc'; }
        send('page', { offset: 0, limit: 200, sortBy, sortDir });
      });
    }
    function renderInspector(p) {
      let html = '<h3>' + esc(p.column || selected || '') + '</h3>';
      html += '<div class="note">' + esc(p.dtype) + ' · ' + esc(p.kind) + '</div>';
      for (const f of ['highNull','constant','highCardinality'])
        if (p.flags && p.flags[f]) html += '<span class="badge">' + f + '</span>';
      html += '<p>nulls: ' + p.nulls + ' (' + (p.nullPct*100).toFixed(1) + '%)<br>unique: ' + p.unique + '</p>';
      if (p.kind === 'numeric') {
        html += '<p>min ' + fmt(p.min) + ' · max ' + fmt(p.max) + '<br>mean ' + fmt(p.mean) + ' · std ' + fmt(p.std) +
          '<br>q25 ' + fmt(p.q25) + ' · q50 ' + fmt(p.q50) + ' · q75 ' + fmt(p.q75) + '</p>';
        html += histHtml(p.histogram.counts);
      } else if (p.kind === 'categorical') {
        html += '<table>' + p.top.map((t) => '<tr><td>' + esc(String(t.value)) + '</td><td>' + t.count + '</td></tr>').join('') + '</table>';
      } else if (p.kind === 'boolean') {
        html += '<p>true ' + p.trueCount + ' · false ' + p.falseCount + '</p>';
      }
      $('insp').innerHTML = html;
    }
    function renderProfileTab() { $('view-profile').innerHTML = '<div class="note">Click a column in the navigator to profile it.</div>'; }

    function histHtml(counts) {
      const max = Math.max(1, ...counts);
      return '<div class="hist">' + counts.map((c) => '<i style="height:' + Math.round(c/max*60) + 'px"></i>').join('') + '</div>';
    }
    function fmt(v){ if(v===null||v===undefined||Number.isNaN(v))return '—'; return Number.isInteger(v)?String(v):Number(v.toPrecision(4)).toString(); }
    function esc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

    window.addEventListener('message', (e) => {
      const m = e.data;
      if (m.type === 'open') {
        if (m.result.shapeKind === 'object') {
          for (const t of document.querySelectorAll('.tab')) if (t.dataset.tab !== 'raw') t.classList.add('hidden');
          document.querySelector('.nav').classList.add('hidden');
          document.querySelector('.insp').classList.add('hidden');
          $('status').textContent = fileName + ' — object (Raw view)';
          showTab('raw');           // showTab already sends rawJson
          return;
        }
        columns = m.result.columns;
        sortBy = null; sortDir = null; selected = null;
        $('status').textContent = fileName + ' — ' + m.result.rowCount + ' rows' + (m.result.sampled ? ' (sampled)' : '');
        $('sampleNote').textContent = m.result.sampled ? 'Showing a sample of the file.' : '';
        renderNav(); renderSchema(); send('page', { offset: 0, limit: 200, sortBy: null, sortDir: null });
      } else if (m.type === 'page') { renderTable(m.result.rows); }
      else if (m.type === 'profile') { renderInspector(Object.assign({ column: selected }, m.result)); }
      else if (m.type === 'raw') { $('raw').textContent = JSON.stringify(m.result.json, null, 2); }
      else if (m.type === 'error') { $('status').textContent = 'Error: ' + m.error; }
    });
    vscode.postMessage({ type: 'ready' });
  </script>
</body></html>`;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
