import * as vscode from 'vscode';
import { PythonEnv } from './backend/PythonEnv';
import { PklEditorProvider } from './providers/PklEditorProvider';
import { H5EditorProvider } from './providers/H5EditorProvider';
import { ExplorerEditorProvider } from './providers/ExplorerEditorProvider';
import { JoblibEditorProvider } from './providers/JoblibEditorProvider';
import { NpyEditorProvider } from './providers/NpyEditorProvider';
import { MsgpackEditorProvider } from './providers/MsgpackEditorProvider';
import { AvroEditorProvider } from './providers/AvroEditorProvider';
import { NetCDFEditorProvider } from './providers/NetCDFEditorProvider';
import { MatEditorProvider } from './providers/MatEditorProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('Data File Viewer extension is now active');

    // Initialize PythonEnv with extension context
    PythonEnv.initialize(context);

    // Register all custom editor providers
    context.subscriptions.push(
        PklEditorProvider.register(context),
        H5EditorProvider.register(context),
        ExplorerEditorProvider.register(context),
        ExplorerEditorProvider.register(context, 'dataFileViewer.feather'),
        ExplorerEditorProvider.register(context, 'dataFileViewer.arrow'),
        JoblibEditorProvider.register(context),
        NpyEditorProvider.register(context),
        MsgpackEditorProvider.register(context),
        AvroEditorProvider.register(context),
        NetCDFEditorProvider.register(context),
        MatEditorProvider.register(context)
    );
}

export function deactivate() {}
