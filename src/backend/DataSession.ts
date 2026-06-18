// src/backend/DataSession.ts
import { ChildProcessWithoutNullStreams } from 'child_process';
import { JsonLineRpc } from './rpc';
// PythonEnv is NOT imported at the top level to avoid pulling in 'vscode' during unit tests.
// It is lazily imported inside create() which only runs in the extension host.

export interface PageArgs {
  offset: number;
  limit: number;
  sortBy?: string | null;
  sortDir?: 'asc' | 'desc' | null;
}

export class DataSession {
  private constructor(
    private readonly child: ChildProcessWithoutNullStreams,
    private readonly rpc: JsonLineRpc,
  ) {}

  static fromChild(child: ChildProcessWithoutNullStreams): DataSession {
    const rpc = new JsonLineRpc(child.stdin, child.stdout);
    const session = new DataSession(child, rpc);
    // Defensive: if child exits unexpectedly, reject all in-flight requests instead of hanging.
    child.on('exit', () => rpc.dispose());
    // Drain stderr so the OS pipe buffer can't fill up and deadlock the child.
    child.stderr.on('data', () => {});
    // Reject pending requests if the process fails to spawn or errors.
    child.on('error', () => rpc.dispose());
    // Swallow write-after-close errors on stdin.
    child.stdin.on('error', () => {});
    return session;
  }

  static async create(extensionPath: string, fileArg: string): Promise<DataSession> {
    // Lazy import keeps 'vscode' out of the module graph during tests.
    const { PythonEnv } = await import('./PythonEnv');
    const child = await PythonEnv.spawnSession(extensionPath, fileArg);
    return DataSession.fromChild(child);
  }

  open(): Promise<any> { return this.rpc.request('open'); }
  page(args: PageArgs): Promise<any> { return this.rpc.request('page', args); }
  profile(column: string): Promise<any> { return this.rpc.request('profile', { column }); }
  rawJson(): Promise<any> { return this.rpc.request('rawJson'); }

  private disposed = false;

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.rpc.dispose();
    try { this.child.kill(); } catch { /* already gone */ }
  }
}
