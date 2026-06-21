import * as vscode from 'vscode';
import { PythonEnv } from './backend/PythonEnv';
import { ExplorerEditorProvider } from './providers/ExplorerEditorProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('Data File Viewer extension is now active');

    // Initialize PythonEnv with extension context
    PythonEnv.initialize(context);

    // Register all custom editor providers
    context.subscriptions.push(
        ExplorerEditorProvider.register(context),
        ExplorerEditorProvider.register(context, 'dataFileViewer.feather'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.arrow'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.npy'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.h5'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.netcdf'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.mat'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.pkl'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.joblib'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.msgpack'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.avro'),
    );
}

export function deactivate() {}
