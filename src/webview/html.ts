// src/webview/html.ts
export function getExplorerHtml(opts: { fileName: string; cspSource: string; nonce: string }): string {
  const { fileName, cspSource, nonce } = opts;
  return `<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  *{box-sizing:border-box;}
  :root{
    --dfv-bg:var(--vscode-editor-background);
    --dfv-fg:var(--vscode-editor-foreground);
    --dfv-muted:var(--vscode-descriptionForeground);
    --dfv-border:var(--vscode-panel-border);
    --dfv-surface:var(--vscode-sideBar-background,var(--vscode-editorWidget-background,var(--vscode-editor-background)));
    --dfv-raised:var(--vscode-editorWidget-background,var(--vscode-editorGroupHeader-tabsBackground,var(--vscode-editor-background)));
    --dfv-hover:var(--vscode-list-hoverBackground);
    --dfv-active:var(--vscode-list-activeSelectionBackground);
    --dfv-active-fg:var(--vscode-list-activeSelectionForeground,var(--vscode-editor-foreground));
    --dfv-focus:var(--vscode-focusBorder);
    --dfv-button:var(--vscode-button-background);
    --dfv-button-fg:var(--vscode-button-foreground);
    --dfv-badge:var(--vscode-badge-background,var(--vscode-inputValidation-warningBackground));
    --dfv-badge-fg:var(--vscode-badge-foreground,var(--vscode-editor-foreground));
    --dfv-warn:var(--vscode-list-warningForeground,var(--vscode-inputValidation-warningForeground,var(--vscode-editorWarning-foreground)));
    --dfv-error:var(--vscode-errorForeground);
    --dfv-chart:var(--vscode-charts-blue,#4e94ce);
  }
  body{
    margin:0;
    height:100vh;
    display:flex;
    flex-direction:column;
    overflow:hidden;
    font-family:var(--vscode-font-family);
    color:var(--dfv-fg);
    background:var(--dfv-bg);
  }
  button{font:inherit;}
  .topbar{
    flex:0 0 auto;
    display:flex;
    align-items:center;
    gap:10px;
    padding:8px 10px;
    border-bottom:1px solid var(--dfv-border);
    background:var(--dfv-surface);
    min-height:45px;
  }
  .tabs{display:flex;align-items:center;gap:3px;min-width:0;}
  .tab,.export{
    min-height:30px;
    border:1px solid transparent;
    border-radius:4px;
    background:transparent;
    color:var(--dfv-fg);
    cursor:pointer;
    padding:5px 10px;
    line-height:18px;
    white-space:nowrap;
  }
  .tab:hover,.export:not(:disabled):hover,.nav-row:not(:disabled):hover{background:var(--dfv-hover);}
  .tab:focus-visible,.export:focus-visible,.nav-row:focus-visible,th:focus-visible{
    outline:1px solid var(--dfv-focus);
    outline-offset:-1px;
  }
  .tab.active{
    background:var(--dfv-raised);
    border-color:var(--dfv-border);
    box-shadow:inset 0 -2px 0 var(--dfv-focus);
  }
  .actions{
    margin-left:auto;
    display:flex;
    align-items:center;
    gap:8px;
    min-width:0;
  }
  .export{
    color:var(--dfv-button-fg);
    background:var(--dfv-button);
    border-color:var(--dfv-button);
  }
  .export:disabled{
    opacity:.48;
    cursor:default;
    background:transparent;
    color:var(--dfv-muted);
    border-color:var(--dfv-border);
  }
  .status{
    min-width:120px;
    max-width:46vw;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:var(--dfv-muted);
    font-size:12px;
  }
  .status.error{color:var(--dfv-error);}
  .layout{
    flex:1 1 auto;
    min-height:0;
    display:grid;
    grid-template-columns:minmax(176px,220px) minmax(0,1fr) minmax(228px,280px);
    background:var(--dfv-bg);
  }
  .raw-only .layout{grid-template-columns:minmax(0,1fr);}
  .raw-only .export{display:none;}
  .nav-pane,.insp{
    min-width:0;
    min-height:0;
    overflow:auto;
    background:var(--dfv-surface);
  }
  .nav-pane{border-right:1px solid var(--dfv-border);}
  .insp{border-left:1px solid var(--dfv-border);padding:10px;}
  .pane-head{
    position:sticky;
    top:0;
    z-index:4;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:8px;
    min-height:34px;
    padding:8px 8px 7px;
    border-bottom:1px solid var(--dfv-border);
    background:var(--dfv-surface);
  }
  .pane-title{
    min-width:0;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    font-size:11px;
    font-weight:600;
    text-transform:uppercase;
    color:var(--dfv-muted);
  }
  .pane-count{
    flex:0 0 auto;
    color:var(--dfv-muted);
    font-size:11px;
    font-variant-numeric:tabular-nums;
  }
  .nav-list{padding:6px;}
  .nav-row{
    width:100%;
    display:grid;
    grid-template-columns:minmax(0,1fr) auto;
    gap:8px;
    align-items:center;
    border:1px solid transparent;
    border-radius:4px;
    padding:5px 6px;
    margin:0 0 3px;
    background:transparent;
    color:var(--dfv-fg);
    text-align:left;
    cursor:pointer;
  }
  .nav-row:disabled{
    cursor:default;
    color:var(--dfv-muted);
    opacity:.82;
  }
  .nav-row.sel{
    background:var(--dfv-active);
    color:var(--dfv-active-fg);
    border-color:transparent;
  }
  .nav-main{
    min-width:0;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    font-size:12px;
  }
  .nav-meta{
    min-width:0;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:var(--dfv-muted);
    font-size:11px;
    font-family:var(--vscode-editor-font-family);
  }
  .nav-row.sel .nav-meta{color:inherit;opacity:.82;}
  .main{
    min-width:0;
    min-height:0;
    overflow:auto;
    padding:10px;
  }
  .view{min-width:0;}
  .notice{
    min-height:22px;
    margin:0 0 8px;
    color:var(--dfv-muted);
    font-size:12px;
  }
  .table-wrap{
    max-width:100%;
    overflow:auto;
    border:1px solid var(--dfv-border);
    border-radius:4px;
    background:var(--dfv-bg);
  }
  table{
    border-collapse:separate;
    border-spacing:0;
    width:max-content;
    min-width:100%;
    font-size:12px;
  }
  th,td{
    border:0;
    border-right:1px solid var(--dfv-border);
    border-bottom:1px solid var(--dfv-border);
    padding:4px 7px;
    text-align:left;
    white-space:nowrap;
    vertical-align:top;
  }
  th:last-child,td:last-child{border-right:0;}
  tr:last-child td{border-bottom:0;}
  th{
    position:sticky;
    top:0;
    z-index:3;
    background:var(--dfv-raised);
    color:var(--dfv-fg);
    font-weight:600;
    cursor:pointer;
  }
  th.idx,td.idx{
    position:sticky;
    left:0;
    width:44px;
    min-width:44px;
    max-width:44px;
    color:var(--dfv-muted);
    background:var(--dfv-raised);
    font-family:var(--vscode-editor-font-family);
    font-variant-numeric:tabular-nums;
    text-align:right;
  }
  td.idx{z-index:2;background:var(--dfv-bg);}
  th.idx{z-index:5;cursor:default;}
  tbody tr:hover td{background:var(--dfv-hover);}
  tbody tr:hover td.idx{background:var(--dfv-hover);}
  .sort{
    margin-left:6px;
    color:var(--dfv-muted);
    font-size:10px;
    font-weight:500;
  }
  .value-null{color:var(--dfv-muted);font-style:italic;}
  .value-special{color:var(--dfv-warn);}
  .empty{
    min-height:140px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    gap:5px;
    padding:22px;
    border:1px dashed var(--dfv-border);
    border-radius:4px;
    color:var(--dfv-muted);
    background:var(--dfv-surface);
  }
  .empty strong{color:var(--dfv-fg);font-weight:600;}
  .inspector-title{
    margin:0 0 4px;
    font-size:14px;
    line-height:1.35;
    word-break:break-word;
  }
  .meta-line{
    margin:0 0 10px;
    color:var(--dfv-muted);
    font-family:var(--vscode-editor-font-family);
    font-size:11px;
    word-break:break-word;
  }
  .badges{display:flex;flex-wrap:wrap;gap:4px;margin:0 0 10px;}
  .badge{
    display:inline-flex;
    align-items:center;
    min-height:19px;
    padding:2px 6px;
    border-radius:3px;
    background:var(--dfv-badge);
    color:var(--dfv-badge-fg);
    font-size:10px;
    font-weight:600;
  }
  .stat-grid{
    display:grid;
    grid-template-columns:1fr auto;
    gap:5px 10px;
    margin:10px 0;
    padding-top:10px;
    border-top:1px solid var(--dfv-border);
  }
  .stat-label{min-width:0;color:var(--dfv-muted);font-size:11px;}
  .stat-value{
    max-width:150px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
    color:var(--dfv-fg);
    font-family:var(--vscode-editor-font-family);
    font-size:11px;
    font-variant-numeric:tabular-nums;
    text-align:right;
  }
  .hist{
    display:flex;
    align-items:flex-end;
    gap:2px;
    height:66px;
    margin-top:10px;
    padding:6px;
    border:1px solid var(--dfv-border);
    border-radius:4px;
    background:var(--dfv-bg);
  }
  .hist i{
    flex:1;
    min-width:3px;
    height:var(--h);
    background:var(--dfv-chart);
    opacity:.88;
  }
  pre{
    margin:0;
    white-space:pre-wrap;
    word-break:break-word;
    font-family:var(--vscode-editor-font-family);
    font-size:12px;
    line-height:1.45;
  }
  .hidden{display:none!important;}
  @media (max-width:900px){
    .layout{grid-template-columns:minmax(150px,190px) minmax(0,1fr);grid-template-rows:minmax(0,1fr) minmax(132px,180px);}
    .insp{grid-column:1 / -1;border-left:0;border-top:1px solid var(--dfv-border);}
  }
  @media (max-width:640px){
    .topbar{align-items:flex-start;}
    .actions{width:100%;margin-left:0;}
    .status{max-width:none;flex:1 1 auto;}
    .layout{grid-template-columns:1fr;grid-template-rows:auto minmax(0,1fr) minmax(120px,170px);}
    .nav-pane{border-right:0;border-bottom:1px solid var(--dfv-border);max-height:150px;}
    .main{padding:8px;}
  }
</style></head>
<body>
  <header class="topbar">
    <nav class="tabs" aria-label="Viewer sections">
      <button class="tab active" type="button" role="tab" data-tab="data" aria-selected="true">Data</button>
      <button class="tab" type="button" role="tab" data-tab="profile" aria-selected="false">Profile</button>
      <button class="tab" type="button" role="tab" data-tab="schema" aria-selected="false">Schema</button>
      <button class="tab" type="button" role="tab" data-tab="raw" aria-selected="false">Raw</button>
    </nav>
    <div class="actions">
      <button class="export" id="exportBtn" type="button" title="Export current view to CSV" disabled>CSV</button>
      <div class="status" id="status" role="status" aria-live="polite" title="${escapeHtml(fileName)}">Loading ${escapeHtml(fileName)}</div>
    </div>
  </header>
  <div class="layout">
    <aside class="nav-pane" id="navPane" aria-label="Data navigator">
      <div class="pane-head"><span class="pane-title" id="navTitle">Fields</span><span class="pane-count" id="navCount"></span></div>
      <div class="nav-list" id="nav"></div>
    </aside>
    <main class="main" aria-label="Data preview">
      <section id="view-data" class="view">
        <div class="notice" id="sampleNote">Loading preview...</div>
        <div class="empty hidden" id="dataEmpty"></div>
        <div class="table-wrap" id="tableWrap"><table id="tbl"></table></div>
      </section>
      <section id="view-profile" class="view hidden"></section>
      <section id="view-schema" class="view hidden"></section>
      <section id="view-raw" class="view hidden"><div class="table-wrap"><pre id="raw">Loading raw JSON...</pre></div></section>
    </main>
    <aside class="insp" id="insp" aria-label="Profile inspector">
      <div class="empty"><strong>No profile selected</strong><span>Select a field, array, or dataset from the navigator.</span></div>
    </aside>
  </div>
  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    const fileName = ${JSON.stringify(fileName)};
    let columns = [], sortBy = null, sortDir = null, selected = null;
    let mode = 'tabular', members = [], selMember = null;
    let tree = [], selNode = null, selLabel = null;
    let lastCols = [], lastRows = [], currentProfileHtml = '';
    const $ = (id) => document.getElementById(id);

    function send(cmd, args) { vscode.postMessage({ type: 'request', cmd, args: args || {} }); }

    function setStatus(text, kind) {
      const el = $('status');
      el.textContent = text;
      el.title = text;
      el.classList.toggle('error', kind === 'error');
    }
    function setNavigator(title, count) {
      $('navTitle').textContent = title;
      $('navCount').textContent = count === undefined || count === null ? '' : String(count);
    }
    function setExportEnabled() {
      $('exportBtn').disabled = !(lastCols && lastCols.length && lastRows && lastRows.length);
    }
    function setTabs(visible) {
      for (const t of document.querySelectorAll('.tab')) {
        const show = visible.indexOf(t.dataset.tab) >= 0;
        t.classList.toggle('hidden', !show);
        t.disabled = !show;
        t.setAttribute('aria-hidden', show ? 'false' : 'true');
      }
    }
    function resetChrome(navTitle) {
      document.body.classList.remove('raw-only');
      $('navPane').classList.remove('hidden');
      $('insp').classList.remove('hidden');
      setTabs(['data','profile','schema','raw']);
      setNavigator(navTitle, '');
      currentProfileHtml = '';
      renderProfileTab();
      showTab('data');
    }
    function showTab(name) {
      if (!name) return;
      for (const t of document.querySelectorAll('.tab')) {
        const active = t.dataset.tab === name && !t.classList.contains('hidden');
        t.classList.toggle('active', active);
        t.setAttribute('aria-selected', active ? 'true' : 'false');
      }
      for (const v of ['data','profile','schema','raw']) $('view-' + v).classList.toggle('hidden', v !== name);
      if (name === 'raw') send('rawJson');
      if (name === 'profile') renderProfileTab();
    }
    document.querySelectorAll('.tab').forEach((t) => t.onclick = () => showTab(t.dataset.tab));
    $('exportBtn').onclick = () => {
      if (!lastCols.length || !lastRows.length) return;
      vscode.postMessage({ type: 'exportCsv', csv: toCsv(lastCols, lastRows), suggestedName: csvName(fileName) });
    };

    function showDataEmpty(title, body) {
      $('dataEmpty').innerHTML = '<strong>' + esc(title) + '</strong><span>' + esc(body) + '</span>';
      $('dataEmpty').classList.remove('hidden');
      $('tableWrap').classList.add('hidden');
    }
    function showDataTable() {
      $('dataEmpty').classList.add('hidden');
      $('tableWrap').classList.remove('hidden');
    }
    function emptyHtml(title, body) {
      return '<div class="empty"><strong>' + esc(title) + '</strong><span>' + esc(body) + '</span></div>';
    }
    function tableWrap(html) { return '<div class="table-wrap">' + html + '</div>'; }
    function stat(label, value) {
      return '<div class="stat-label">' + esc(label) + '</div><div class="stat-value" title="' + esc(String(value)) + '">' + esc(String(value)) + '</div>';
    }
    function valueHtml(v) {
      if (v === null || v === undefined) return '<span class="value-null">null</span>';
      if (typeof v === 'number' && !Number.isFinite(v)) return '<span class="value-special">' + esc(String(v)) + '</span>';
      const s = String(v);
      if (s === 'NaN' || s === 'Infinity' || s === '-Infinity') return '<span class="value-special">' + esc(s) + '</span>';
      return esc(s);
    }

    function renderNav() {
      $('nav').innerHTML = '';
      setNavigator('Fields', columns.length);
      if (!columns.length) {
        $('nav').innerHTML = emptyHtml('No fields', 'This file did not expose tabular columns.');
        return;
      }
      columns.forEach((c) => {
        const d = document.createElement('button');
        d.type = 'button';
        d.className = 'nav-row' + (c.name === selected ? ' sel' : '');
        d.title = c.name + ' | ' + c.dtype;
        d.innerHTML = '<span class="nav-main">' + esc(c.name) + '</span><span class="nav-meta">' + esc(c.dtype) + '</span>';
        d.onclick = () => { selected = c.name; renderNav(); send('profile', { column: c.name }); };
        $('nav').appendChild(d);
      });
    }
    function renderSchema() {
      $('view-schema').innerHTML = tableWrap('<table><thead><tr><th>Column</th><th>Dtype</th></tr></thead><tbody>' +
        columns.map((c) => '<tr><td>' + esc(c.name) + '</td><td>' + esc(c.dtype) + '</td></tr>').join('') + '</tbody></table>');
    }
    function renderTable(rows) {
      lastCols = columns.map((c) => c.name); lastRows = rows || [];
      setExportEnabled();
      if (!columns.length || !lastRows.length) {
        $('tbl').innerHTML = '';
        showDataEmpty('No rows to preview', columns.length ? 'The current page is empty.' : 'This file did not expose tabular columns.');
        return;
      }
      showDataTable();
      const head = '<thead><tr><th class="idx">#</th>' + columns.map((c) => {
        const sort = c.name === sortBy ? '<span class="sort">' + (sortDir === 'desc' ? 'desc' : 'asc') + '</span>' : '';
        return '<th tabindex="0" data-c="' + esc(c.name) + '" title="Sort by ' + esc(c.name) + '">' + esc(c.name) + sort + '</th>';
      }).join('') + '</tr></thead>';
      const body = '<tbody>' + lastRows.map((r, i) => '<tr><td class="idx">' + i + '</td>' + r.map((v) =>
        '<td>' + valueHtml(v) + '</td>').join('') + '</tr>').join('') + '</tbody>';
      $('tbl').innerHTML = head + body;
      $('tbl').querySelectorAll('th[data-c]').forEach((th) => {
        th.onclick = () => sortColumn(th.dataset.c);
        th.onkeydown = (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); sortColumn(th.dataset.c); } };
      });
    }
    function sortColumn(c) {
      if (sortBy === c) sortDir = sortDir === 'desc' ? 'asc' : 'desc'; else { sortBy = c; sortDir = 'asc'; }
      send('page', { offset: 0, limit: 200, sortBy, sortDir });
    }
    function flagsHtml(flags) {
      if (!flags) return '';
      const labels = { highNull: 'High nulls', constant: 'Constant', highCardinality: 'High cardinality' };
      const items = Object.keys(labels).filter((k) => flags[k]).map((k) => '<span class="badge">' + labels[k] + '</span>');
      return items.length ? '<div class="badges">' + items.join('') + '</div>' : '';
    }
    function renderInspector(p) {
      let html = '<h3 class="inspector-title">' + esc(p.column || selected || 'Column profile') + '</h3>';
      html += '<div class="meta-line">' + esc(p.dtype || '-') + ' | ' + esc(p.kind || '-') + '</div>';
      html += flagsHtml(p.flags);
      html += '<div class="stat-grid">';
      html += stat('Nulls', fmt(p.nulls) + ' (' + fmtPct(p.nullPct) + ')');
      html += stat('Unique', fmt(p.unique));
      if (p.kind === 'numeric') {
        html += stat('Min', fmt(p.min)) + stat('Max', fmt(p.max)) + stat('Mean', fmt(p.mean)) + stat('Std', fmt(p.std));
        html += stat('Q25', fmt(p.q25)) + stat('Q50', fmt(p.q50)) + stat('Q75', fmt(p.q75));
      } else if (p.kind === 'boolean') {
        html += stat('True', fmt(p.trueCount)) + stat('False', fmt(p.falseCount));
      }
      html += '</div>';
      if (p.kind === 'numeric' && p.histogram) html += histHtml(p.histogram.counts);
      if (p.kind === 'categorical' && p.top) {
        html += tableWrap('<table><thead><tr><th>Value</th><th>Count</th></tr></thead><tbody>' +
          p.top.map((t) => '<tr><td>' + valueHtml(t.value) + '</td><td>' + fmt(t.count) + '</td></tr>').join('') + '</tbody></table>');
      }
      currentProfileHtml = html;
      $('insp').innerHTML = html;
      renderProfileTab();
    }
    function renderProfileTab() {
      $('view-profile').innerHTML = currentProfileHtml || emptyHtml('No profile selected', 'Pick a field, array, or dataset from the navigator.');
    }

    function fmtShape(s){ return (!s || s.length === 0) ? '()' : s.join(' x '); }

    function renderMemberNav() {
      $('nav').innerHTML = '';
      setNavigator('Arrays', members.length);
      if (!members.length) {
        $('nav').innerHTML = emptyHtml('No arrays', 'This file did not expose array members.');
        return;
      }
      members.forEach((mem) => {
        const d = document.createElement('button');
        d.type = 'button';
        d.className = 'nav-row' + (mem.name === selMember ? ' sel' : '');
        d.title = mem.name + ' | ' + mem.dtype + ' | ' + fmtShape(mem.shape);
        d.innerHTML = '<span class="nav-main">' + esc(mem.name) + '</span><span class="nav-meta">' + esc(mem.dtype + ' ' + fmtShape(mem.shape)) + '</span>';
        d.onclick = () => selectMember(mem.name);
        $('nav').appendChild(d);
      });
    }
    function selectMember(name) {
      lastCols = []; lastRows = []; setExportEnabled();
      selMember = name; selLabel = name; renderMemberNav();
      send('page', { column: name, offset: 0, limit: 200 });
      send('profile', { column: name });
    }
    function renderArraySchema() {
      $('view-schema').innerHTML = tableWrap('<table><thead><tr><th>Array</th><th>Dtype</th><th>Shape</th><th>Size</th></tr></thead><tbody>' +
        members.map((mem) => '<tr><td>' + esc(mem.name) + '</td><td>' + esc(mem.dtype) +
          '</td><td>' + esc(fmtShape(mem.shape)) + '</td><td>' + mem.size + '</td></tr>').join('') + '</tbody></table>');
    }
    function renderArrayGrid(res) {
      lastCols = res.columns || []; lastRows = res.rows || [];
      setExportEnabled();
      const notes = [];
      if (res.sliced) notes.push('N-D array - showing slice ' + res.sliceLabel);
      if (res.colsTruncated) notes.push('columns truncated to ' + res.columns.length + ' of ' + res.colCount);
      if (res.rowCount > res.rows.length) notes.push('showing first ' + res.rows.length + ' of ' + res.rowCount + ' rows');
      $('sampleNote').textContent = notes.join(' | ');
      if (!lastRows.length) {
        $('tbl').innerHTML = '';
        showDataEmpty('No array values to preview', 'The selected array returned no rows.');
        return;
      }
      showDataTable();
      const head = '<thead><tr><th class="idx">#</th>' + res.columns.map((c) => '<th>' + esc(c) + '</th>').join('') + '</tr></thead>';
      const body = '<tbody>' + res.rows.map((r, i) => '<tr><td class="idx">' + i + '</td>' + r.map((v) =>
        '<td>' + valueHtml(v) + '</td>').join('') + '</tr>').join('') + '</tbody>';
      $('tbl').innerHTML = head + body;
    }
    function renderArrayInspector(p) {
      let html = '<h3 class="inspector-title">' + esc(selLabel || 'Array profile') + '</h3>';
      html += '<div class="meta-line">' + esc(p.dtype || '-') + ' | ' + esc(p.kind || '-') + '</div>';
      html += '<div class="stat-grid">';
      html += stat('Shape', fmtShape(p.shape));
      html += stat('Dimensions', fmt(p.ndim));
      html += stat('Size', fmt(p.size));
      if (p.kind === 'numeric') {
        html += stat('Min', fmt(p.min)) + stat('Max', fmt(p.max)) + stat('Mean', fmt(p.mean)) + stat('Std', fmt(p.std));
        html += stat('NaN', fmt(p.nanCount)) + stat('Inf', fmt(p.infCount)) + stat('Finite', fmt(p.finite));
      }
      html += '</div>';
      if (p.kind === 'numeric' && p.histogram) html += histHtml(p.histogram.counts);
      currentProfileHtml = html;
      $('insp').innerHTML = html;
      renderProfileTab();
    }

    function renderTreeNav() {
      $('nav').innerHTML = '';
      setNavigator('Datasets', tree.filter((n) => n.kind === 'leaf').length);
      if (!tree.length) {
        $('nav').innerHTML = emptyHtml('No datasets', 'This hierarchical file did not expose previewable leaves.');
        return;
      }
      tree.forEach((n) => {
        const isLeaf = n.kind === 'leaf';
        const d = document.createElement('button');
        d.type = 'button';
        d.className = 'nav-row' + (n.path === selNode ? ' sel' : '');
        d.style.paddingLeft = (6 + n.depth * 12) + 'px';
        d.disabled = !isLeaf;
        const prefix = isLeaf ? '' : '> ';
        const meta = isLeaf ? ((n.dtype || '-') + ' ' + fmtShape(n.shape)) : 'group';
        d.title = n.path + (isLeaf ? ' | ' + meta : '');
        d.innerHTML = '<span class="nav-main">' + esc(prefix + n.name) + '</span><span class="nav-meta">' + esc(meta) + '</span>';
        if (isLeaf) d.onclick = () => selectNode(n.path);
        $('nav').appendChild(d);
      });
    }
    function selectNode(path) {
      lastCols = []; lastRows = []; setExportEnabled();
      selNode = path; selLabel = path; renderTreeNav();
      send('page', { column: path, offset: 0, limit: 200 });
      send('profile', { column: path });
    }
    function renderHierSchema() {
      $('view-schema').innerHTML = tableWrap('<table><thead><tr><th>Node</th><th>Kind</th><th>Dtype</th><th>Shape</th></tr></thead><tbody>' +
        tree.map((n) => '<tr><td>' + esc(n.path) + '</td><td>' + esc(n.kind) + '</td><td>' +
          esc(n.dtype || '') + '</td><td>' + esc(n.kind === 'leaf' ? fmtShape(n.shape) : '') +
          '</td></tr>').join('') + '</tbody></table>');
    }

    function histHtml(counts) {
      counts = counts || [];
      if (!counts.length) return '';
      const max = Math.max(1, ...counts);
      return '<div class="hist" aria-label="Histogram">' + counts.map((c) =>
        '<i style="--h:' + Math.max(1, Math.round(c/max*54)) + 'px" title="' + esc(String(c)) + '"></i>').join('') + '</div>';
    }
    function fmt(v){ if(v===null||v===undefined)return '-'; if(typeof v!=='number')return String(v); if(Number.isNaN(v))return '-'; return Number.isInteger(v)?String(v):Number(v.toPrecision(4)).toString(); }
    function fmtPct(v){ return typeof v === 'number' ? (v * 100).toFixed(1) + '%' : '-'; }
    function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
    function csvField(v){ if(v===null||v===undefined)return ''; const s=String(v); return /[",\\r\\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s; }
    function toCsv(cols, rows){ const lines=[cols.map(csvField).join(',')]; for(const r of rows) lines.push(r.map(csvField).join(',')); return lines.join('\\r\\n'); }
    function csvName(fn){ const dot=fn.lastIndexOf('.'); return (dot>0?fn.slice(0,dot):fn)+'.csv'; }

    window.addEventListener('message', (e) => {
      const m = e.data;
      if (m.type === 'open') {
        lastCols = []; lastRows = []; setExportEnabled();
        if (m.result.shapeKind === 'object') {
          document.body.classList.add('raw-only');
          setTabs(['raw']);
          $('navPane').classList.add('hidden');
          $('insp').classList.add('hidden');
          setStatus(fileName + ' - object (Raw view)');
          $('raw').textContent = 'Loading raw JSON...';
          showTab('raw');
          return;
        }
        if (m.result.shapeKind === 'array') {
          mode = 'array';
          members = m.result.members;
          selMember = null;
          resetChrome('Arrays');
          setStatus(fileName + ' - ' + members.length + ' array' + (members.length === 1 ? '' : 's'));
          renderMemberNav(); renderArraySchema();
          if (members.length) selectMember(members[0].name); else showDataEmpty('No arrays', 'This file did not expose array members.');
          return;
        }
        if (m.result.shapeKind === 'hierarchical') {
          mode = 'hierarchical';
          tree = m.result.tree;
          selNode = null;
          const leaves = tree.filter((n) => n.kind === 'leaf');
          resetChrome('Datasets');
          setStatus(fileName + ' - ' + leaves.length + ' dataset' + (leaves.length === 1 ? '' : 's'));
          renderTreeNav(); renderHierSchema();
          if (leaves.length) selectNode(leaves[0].path); else showDataEmpty('No datasets', 'This file did not expose previewable leaves.');
          return;
        }
        mode = 'tabular';
        columns = m.result.columns;
        sortBy = null; sortDir = null; selected = null;
        resetChrome('Fields');
        setStatus(fileName + ' - ' + m.result.rowCount + ' rows' + (m.result.sampled ? ' (sampled)' : ''));
        $('sampleNote').textContent = m.result.sampled ? 'Showing a sampled preview of the file.' : '';
        renderNav(); renderSchema(); send('page', { offset: 0, limit: 200, sortBy: null, sortDir: null });
      } else if (m.type === 'page') { (mode === 'array' || mode === 'hierarchical') ? renderArrayGrid(m.result) : renderTable(m.result.rows); }
      else if (m.type === 'profile') { (mode === 'array' || mode === 'hierarchical') ? renderArrayInspector(m.result) : renderInspector(Object.assign({ column: selected }, m.result)); }
      else if (m.type === 'raw') { $('raw').textContent = JSON.stringify(m.result.json, null, 2); }
      else if (m.type === 'status') { setStatus(m.text); }
      else if (m.type === 'error') { setStatus('Error: ' + m.error, 'error'); showDataEmpty('Could not read this file', m.error); }
    });
    vscode.postMessage({ type: 'ready' });
  </script>
</body></html>`;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
