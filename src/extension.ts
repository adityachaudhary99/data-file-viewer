import * as vscode from 'vscode';
import { PklEditorProvider } from './providers/PklEditorProvider';
import { H5EditorProvider } from './providers/H5EditorProvider';
import { ParquetEditorProvider } from './providers/ParquetEditorProvider';
import { FeatherEditorProvider } from './providers/FeatherEditorProvider';
import { JoblibEditorProvider } from './providers/JoblibEditorProvider';
import { NpyEditorProvider } from './providers/NpyEditorProvider';
import { MsgpackEditorProvider } from './providers/MsgpackEditorProvider';
import { ArrowEditorProvider } from './providers/ArrowEditorProvider';
import { AvroEditorProvider } from './providers/AvroEditorProvider';
import { NetCDFEditorProvider } from './providers/NetCDFEditorProvider';
import { MatEditorProvider } from './providers/MatEditorProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('Data File Viewer extension is now active');

    // Register all custom editor providers
    context.subscriptions.push(
        PklEditorProvider.register(context),
        H5EditorProvider.register(context),
        ParquetEditorProvider.register(context),
        FeatherEditorProvider.register(context),
        JoblibEditorProvider.register(context),
        NpyEditorProvider.register(context),
        MsgpackEditorProvider.register(context),
        ArrowEditorProvider.register(context),
        AvroEditorProvider.register(context),
        NetCDFEditorProvider.register(context),
        MatEditorProvider.register(context)
    );
}

export function deactivate() {}
