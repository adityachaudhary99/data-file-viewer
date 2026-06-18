// src/backend/rpc.ts
type Pending = { resolve: (v: any) => void; reject: (e: Error) => void };

export class JsonLineRpc {
  private nextId = 1;
  private pending = new Map<number, Pending>();
  private buffer = '';

  constructor(
    private readonly writable: NodeJS.WritableStream,
    readable: NodeJS.ReadableStream,
  ) {
    readable.on('data', (chunk) => this.onData(chunk.toString()));
  }

  request(cmd: string, args: object = {}): Promise<any> {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.writable.write(JSON.stringify({ ...args, id, cmd }) + '\n');
    });
  }

  private onData(text: string): void {
    this.buffer += text;
    let nl: number;
    while ((nl = this.buffer.indexOf('\n')) >= 0) {
      const line = this.buffer.slice(0, nl).trim();
      this.buffer = this.buffer.slice(nl + 1);
      if (!line) continue;
      let reply: any;
      try { reply = JSON.parse(line); } catch { continue; }
      const p = this.pending.get(reply.id);
      if (!p) continue;
      this.pending.delete(reply.id);
      if (reply.ok) p.resolve(reply.result);
      else p.reject(new Error(reply.error || 'unknown error'));
    }
  }

  dispose(): void {
    for (const p of this.pending.values()) p.reject(new Error('disposed'));
    this.pending.clear();
  }
}
