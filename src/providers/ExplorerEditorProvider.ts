// src/providers/ExplorerEditorProvider.ts
import * as vscode from 'vscode';
import * as path from 'path';
import { DataSession, PageArgs } from '../backend/DataSession';
import { PythonEnv } from '../backend/PythonEnv';
import { getExplorerHtml } from '../webview/html';

export class ExplorerEditorProvider implements vscode.CustomReadonlyEditorProvider {
  public static readonly viewType = 'dataFileViewer.parquet';

  public static register(context: vscode.ExtensionContext): vscode.Disposable {
    return vscode.window.registerCustomEditorProvider(
      ExplorerEditorProvider.viewType,
      new ExplorerEditorProvider(context),
      { webviewOptions: { retainContextWhenHidden: true }, supportsMultipleEditorsPerDocument: false },
    );
  }

  constructor(private readonly context: vscode.ExtensionContext) {}

  async openCustomDocument(uri: vscode.Uri): Promise<vscode.CustomDocument> {
    return { uri, dispose: () => {} };
  }

  async resolveCustomEditor(document: vscode.CustomDocument, panel: vscode.WebviewPanel): Promise<void> {
    panel.webview.options = { enableScripts: true };

    const ok = await PythonEnv.ensureReady();
    if (!ok) {
      panel.webview.html = `<body style="padding:16px;font-family:sans-serif">Python packages are required. Install with:<br><code>pip install pandas pyarrow</code></body>`;
      return;
    }

    let session: DataSession;
    try {
      session = await DataSession.create(this.context.extensionPath, document.uri.fsPath);
    } catch (err) {
      panel.webview.html = `<body style="padding:16px">Failed to start data session: ${String(err)}</body>`;
      return;
    }

    const nonce = String(Date.now()) + Math.random().toString(36).slice(2);

    const sub = panel.webview.onDidReceiveMessage(async (msg) => {
      try {
        if (msg.type === 'ready') {
          panel.webview.postMessage({ type: 'open', result: await session.open() });
          return;
        }
        if (msg.type === 'request') {
          const result = await dispatch(session, msg.cmd, msg.args);
          const outType = msg.cmd === 'rawJson' ? 'raw' : msg.cmd;
          panel.webview.postMessage({ type: outType, result });
        }
      } catch (err) {
        panel.webview.postMessage({ type: 'error', error: String(err) });
      }
    });

    panel.webview.html = getExplorerHtml({
      fileName: path.basename(document.uri.fsPath),
      cspSource: panel.webview.cspSource,
      nonce,
    });

    panel.onDidDispose(() => { sub.dispose(); session.dispose(); });
  }
}

function dispatch(session: DataSession, cmd: string, args: any): Promise<any> {
  switch (cmd) {
    case 'page': return session.page(args as PageArgs);
    case 'profile': return session.profile(args.column);
    case 'rawJson': return session.rawJson();
    default: return Promise.reject(new Error('unknown cmd ' + cmd));
  }
}
