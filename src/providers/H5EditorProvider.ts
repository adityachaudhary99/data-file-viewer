import * as vscode from 'vscode';
import * as path from 'path';
import { BaseEditorProvider } from '../utils/BaseEditorProvider';
import { PythonRunner } from '../utils/PythonRunner';

export class H5EditorProvider extends BaseEditorProvider {
    public static readonly viewType = 'dataFileViewer.h5';

    public static register(context: vscode.ExtensionContext): vscode.Disposable {
        const provider = new H5EditorProvider(context);
        return BaseEditorProvider.register(context, H5EditorProvider.viewType, provider);
    }

    constructor(private readonly context: vscode.ExtensionContext) {
        super();
    }

    protected async convertToJson(uri: vscode.Uri): Promise<any> {
        const scriptPath = path.join(this.context.extensionPath, 'python', 'convert_h5.py');
        const output = await PythonRunner.runScript(scriptPath, [uri.fsPath]);
        return JSON.parse(output);
    }

    protected getFileTypeDisplay(): string {
        return 'HDF5 (.h5/.hdf5)';
    }
}
