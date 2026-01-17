import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { PythonRunner } from './PythonRunner';

export abstract class BaseEditorProvider implements vscode.CustomReadonlyEditorProvider {
    protected static viewType: string;

    public static register(context: vscode.ExtensionContext, viewType: string, provider: BaseEditorProvider): vscode.Disposable {
        return vscode.window.registerCustomEditorProvider(
            viewType,
            provider,
            {
                webviewOptions: {
                    retainContextWhenHidden: true,
                },
                supportsMultipleEditorsPerDocument: false,
            }
        );
    }

    async openCustomDocument(
        uri: vscode.Uri,
        openContext: vscode.CustomDocumentOpenContext,
        token: vscode.CancellationToken
    ): Promise<vscode.CustomDocument> {
        return { uri, dispose: () => {} };
    }

    async resolveCustomEditor(
        document: vscode.CustomDocument,
        webviewPanel: vscode.WebviewPanel,
        token: vscode.CancellationToken
    ): Promise<void> {
        webviewPanel.webview.options = {
            enableScripts: true,
        };

        webviewPanel.webview.html = this.getLoadingHtml();

        // Don't wrap in try-catch yet - let package check happen first
        const packagesInstalled = await PythonRunner.checkAndInstallPackages();
        if (!packagesInstalled) {
            webviewPanel.webview.html = this.getErrorHtml(
                'Python packages are required. Please install them:\n\n' +
                'pip install numpy pandas h5py pyarrow msgpack joblib avro-python3 netCDF4 scipy'
            );
            return;
        }

        try {
            const jsonData = await this.convertToJson(document.uri);
            webviewPanel.webview.html = this.getWebviewContent(jsonData, document.uri);
        } catch (error) {
            webviewPanel.webview.html = this.getErrorHtml(error instanceof Error ? error.message : String(error));
        }
    }

    protected abstract convertToJson(uri: vscode.Uri): Promise<any>;

    protected abstract getFileTypeDisplay(): string;

    protected getLoadingHtml(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            font-family: var(--vscode-font-family);
        }
        .loader {
            text-align: center;
        }
        .spinner {
            border: 4px solid var(--vscode-progressBar-background);
            border-top: 4px solid var(--vscode-progressBar-foreground);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="loader">
        <div class="spinner"></div>
        <p>Loading ${this.getFileTypeDisplay()} file...</p>
    </div>
</body>
</html>`;
    }

    protected getErrorHtml(errorMessage: string): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body {
            padding: 20px;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            font-family: var(--vscode-font-family);
        }
        .error-container {
            background-color: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            border-radius: 4px;
            padding: 20px;
            margin: 20px 0;
        }
        .error-title {
            color: var(--vscode-errorForeground);
            font-weight: bold;
            margin-bottom: 10px;
        }
        .error-message {
            font-family: var(--vscode-editor-font-family);
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .requirements {
            margin-top: 20px;
            padding: 15px;
            background-color: var(--vscode-textBlockQuote-background);
            border-left: 4px solid var(--vscode-textBlockQuote-border);
        }
        code {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: var(--vscode-editor-font-family);
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-title">Failed to load ${this.getFileTypeDisplay()} file</div>
        <div class="error-message">${this.escapeHtml(errorMessage)}</div>
    </div>
    <div class="requirements">
        <strong>Requirements:</strong>
        <ul>
            <li>Python 3.7 or higher must be installed</li>
            <li>Required packages: <code>numpy pandas h5py pyarrow msgpack</code></li>
            <li>Install with: <code>pip install numpy pandas h5py pyarrow msgpack</code></li>
        </ul>
    </div>
</body>
</html>`;
    }

    protected getWebviewContent(jsonData: any, uri: vscode.Uri): string {
        const jsonString = JSON.stringify(jsonData, null, 2);
        const fileName = path.basename(uri.fsPath);
        
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${fileName}</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            padding: 0;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            font-family: var(--vscode-font-family);
            overflow: hidden;
        }
        .header {
            padding: 10px 20px;
            background-color: var(--vscode-editorGroupHeader-tabsBackground);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-info {
            font-size: 14px;
        }
        .file-name {
            font-weight: bold;
            margin-right: 10px;
        }
        .file-type {
            color: var(--vscode-descriptionForeground);
        }
        .controls {
            display: flex;
            gap: 10px;
        }
        button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 6px 14px;
            border-radius: 2px;
            cursor: pointer;
            font-size: 13px;
            font-family: var(--vscode-font-family);
        }
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        button:active {
            opacity: 0.8;
        }
        .content {
            height: calc(100vh - 52px);
            overflow: auto;
            padding: 20px;
        }
        pre {
            margin: 0;
            font-family: var(--vscode-editor-font-family);
            font-size: var(--vscode-editor-font-size, 14px);
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .json-key {
            color: var(--vscode-symbolIcon-propertyForeground, #9cdcfe);
        }
        .json-string {
            color: var(--vscode-debugTokenExpression-string, #ce9178);
        }
        .json-number {
            color: var(--vscode-debugTokenExpression-number, #b5cea8);
        }
        .json-boolean {
            color: var(--vscode-debugTokenExpression-boolean, #569cd6);
        }
        .json-null {
            color: var(--vscode-debugTokenExpression-error, #f44747);
        }
        .stats {
            margin-top: 10px;
            padding: 10px;
            background-color: var(--vscode-textBlockQuote-background);
            border-left: 4px solid var(--vscode-textBlockQuote-border);
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="file-info">
            <span class="file-name">${this.escapeHtml(fileName)}</span>
            <span class="file-type">${this.getFileTypeDisplay()} → JSON</span>
        </div>
        <div class="controls">
            <button onclick="copyToClipboard()">Copy JSON</button>
            <button onclick="toggleSimplify()" id="simplifyBtn">Simplify JSON</button>
            <button onclick="toggleCollapse()">Collapse All</button>
            <button onclick="toggleExpand()">Expand All</button>
        </div>
    </div>
    <div class="content">
        <pre id="json-content">${this.syntaxHighlight(jsonString)}</pre>
        <div class="stats">
            File size: ${this.formatBytes(fs.statSync(uri.fsPath).size)} | 
            JSON size: ${this.formatBytes(jsonString.length)} | 
            Type: ${this.getFileTypeDisplay()}
        </div>
    </div>
    <script>
        const jsonData = ${jsonString};
        let isSimplified = false;
        
        function simplifyData(obj) {
            if (obj === null || obj === undefined) return obj;
            
            if (Array.isArray(obj)) {
                return obj.map(item => simplifyData(item));
            }
            
            if (typeof obj === 'object') {
                // Handle special type wrappers
                if (obj._type === 'numpy.ndarray' && obj.data) {
                    return simplifyData(obj.data);
                }
                if (obj._type === 'pandas.DataFrame' && obj.data) {
                    return simplifyData(obj.data);
                }
                if (obj._type === 'pandas.Series' && obj.data) {
                    return simplifyData(obj.data);
                }
                if (obj._type === 'tuple' && obj.data) {
                    return simplifyData(obj.data);
                }
                if (obj._type === 'set' && obj.data) {
                    return simplifyData(obj.data);
                }
                
                // Remove metadata fields
                const simplified = {};
                for (let key in obj) {
                    if (!key.startsWith('_') && key !== 'file_type' && key !== 'metadata' && key !== 'schema') {
                        simplified[key] = simplifyData(obj[key]);
                    }
                }
                return simplified;
            }
            
            return obj;
        }
        
        function toggleSimplify() {
            isSimplified = !isSimplified;
            const btn = document.getElementById('simplifyBtn');
            const data = isSimplified ? simplifyData(jsonData) : jsonData;
            
            btn.textContent = isSimplified ? 'Show Details' : 'Simplify';
            document.getElementById('json-content').innerHTML = syntaxHighlight(JSON.stringify(data, null, 2));
        }
        
        function copyToClipboard() {
            const data = isSimplified ? simplifyData(jsonData) : jsonData;
            navigator.clipboard.writeText(JSON.stringify(data, null, 2)).then(() => {
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied!';
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            });
        }
        
        function toggleCollapse() {
            const data = isSimplified ? simplifyData(jsonData) : jsonData;
            document.getElementById('json-content').innerHTML = syntaxHighlight(JSON.stringify(data));
        }
        
        function toggleExpand() {
            const data = isSimplified ? simplifyData(jsonData) : jsonData;
            document.getElementById('json-content').innerHTML = syntaxHighlight(JSON.stringify(data, null, 2));
        }
        
        function syntaxHighlight(json) {
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/(\"(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\\"])*\"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function (match) {
                let cls = 'json-number';
                if (/^\"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'json-key';
                    } else {
                        cls = 'json-string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'json-boolean';
                } else if (/null/.test(match)) {
                    cls = 'json-null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        }
    </script>
</body>
</html>`;
    }

    protected escapeHtml(unsafe: string): string {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    protected syntaxHighlight(json: string): string {
        json = this.escapeHtml(json);
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
            let cls = 'json-number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'json-key';
                } else {
                    cls = 'json-string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'json-boolean';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return `<span class="${cls}">${match}</span>`;
        });
    }

    protected formatBytes(bytes: number): string {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
}
