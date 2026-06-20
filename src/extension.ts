import * as vscode from 'vscode';
import { PythonEnv } from './backend/PythonEnv';
import { H5EditorProvider } from './providers/H5EditorProvider';
import { ExplorerEditorProvider } from './providers/ExplorerEditorProvider';
import { NetCDFEditorProvider } from './providers/NetCDFEditorProvider';
import { MatEditorProvider } from './providers/MatEditorProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('Data File Viewer extension is now active');

    // Initialize PythonEnv with extension context
    PythonEnv.initialize(context);

    // Register all custom editor providers
    context.subscriptions.push(
        H5EditorProvider.register(context),
        ExplorerEditorProvider.register(context),
        ExplorerEditorProvider.register(context, 'dataFileViewer.feather'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.arrow'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.npy'),
        NetCDFEditorProvider.register(context),
        MatEditorProvider.register(context),
        ExplorerEditorProvider.register(context, 'dataFileViewer.pkl'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.joblib'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.msgpack'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.avro'),
    );
}

export function deactivate() {}
