import * as vscode from 'vscode';
import * as path from 'path';
import { BaseEditorProvider } from '../utils/BaseEditorProvider';
import { PythonRunner } from '../utils/PythonRunner';

export class NpyEditorProvider extends BaseEditorProvider {
    public static readonly viewType = 'dataFileViewer.npy';

    public static register(context: vscode.ExtensionContext): vscode.Disposable {
        const provider = new NpyEditorProvider(context);
        return BaseEditorProvider.register(context, NpyEditorProvider.viewType, provider);
    }

    constructor(private readonly context: vscode.ExtensionContext) {
        super();
    }

    protected async convertToJson(uri: vscode.Uri): Promise<any> {
        const scriptPath = path.join(this.context.extensionPath, 'python', 'convert_npy.py');
        const output = await PythonRunner.runScript(scriptPath, [uri.fsPath]);
        return JSON.parse(output);
    }

    protected getFileTypeDisplay(): string {
        return 'NumPy (.npy/.npz)';
    }
}
