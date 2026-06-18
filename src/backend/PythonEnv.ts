// src/backend/PythonEnv.ts
import * as vscode from 'vscode';
import * as path from 'path';
import { spawn, ChildProcessWithoutNullStreams } from 'child_process';
import { PythonRunner } from '../utils/PythonRunner';

export class PythonEnv {
  static initialize(context: vscode.ExtensionContext): void {
    PythonRunner.initialize(context);
  }

  static async ensureReady(): Promise<boolean> {
    return PythonRunner.checkAndInstallPackages();
  }

  static async spawnSession(
    extensionPath: string,
    fileArg: string,
  ): Promise<ChildProcessWithoutNullStreams> {
    const python = await PythonRunner.findPython();
    const script = path.join(extensionPath, 'python', 'session.py');
    return spawn(python, [script, fileArg], { stdio: 'pipe' });
  }
}
