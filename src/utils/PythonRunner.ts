import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execAsync = promisify(exec);

export class PythonRunner {
    private static pythonPath: string | null = null;

    static async findPython(): Promise<string> {
        if (this.pythonPath) {
            return this.pythonPath;
        }

        // Get workspace folders
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            const workspaceRoot = workspaceFolders[0].uri.fsPath;
            
            // Check for .venv in workspace (Windows)
            const venvPaths = [
                path.join(workspaceRoot, '.venv', 'Scripts', 'python.exe'),
                path.join(workspaceRoot, '.venv', 'bin', 'python'),
                path.join(workspaceRoot, 'venv', 'Scripts', 'python.exe'),
                path.join(workspaceRoot, 'venv', 'bin', 'python'),
            ];
            
            for (const venvPath of venvPaths) {
                if (fs.existsSync(venvPath)) {
                    this.pythonPath = `"${venvPath}"`;
                    return this.pythonPath;
                }
            }
        }

        // Try to get Python from VS Code Python extension
        const pythonExtension = vscode.extensions.getExtension('ms-python.python');
        if (pythonExtension) {
            try {
                if (!pythonExtension.isActive) {
                    await pythonExtension.activate();
                }
                const pythonPath = pythonExtension.exports?.settings?.getExecutionDetails?.()?.execCommand?.[0];
                if (pythonPath) {
                    this.pythonPath = pythonPath;
                    return pythonPath;
                }
            } catch (error) {
                // Continue to other methods
            }
        }

        // Try common Python commands
        const pythonCommands = ['python3', 'python', 'py'];
        
        for (const cmd of pythonCommands) {
            try {
                const { stdout } = await execAsync(`${cmd} --version`);
                if (stdout.includes('Python 3')) {
                    this.pythonPath = cmd;
                    return cmd;
                }
            } catch (error) {
                continue;
            }
        }

        throw new Error('Python 3 not found. Please install Python 3.7 or higher.');
    }

    static async runScript(scriptPath: string, args: string[] = []): Promise<string> {
        const python = await this.findPython();
        const command = `${python} "${scriptPath}" ${args.map(arg => `"${arg}"`).join(' ')}`;
        
        try {
            const { stdout, stderr } = await execAsync(command, {
                maxBuffer: 50 * 1024 * 1024, // 50MB buffer for large outputs
                timeout: 30000 // 30 second timeout
            });
            
            if (stderr && !stderr.includes('Warning')) {
                console.error('Python stderr:', stderr);
            }
            
            return stdout;
        } catch (error: any) {
            const errorMessage = error.stderr || error.message || String(error);
            
            // Check for missing package errors
            if (errorMessage.includes('ModuleNotFoundError') || errorMessage.includes('No module named')) {
                const match = errorMessage.match(/No module named ['"](.+?)['"]/);
                const moduleName = match ? match[1] : 'required package';
                throw new Error(
                    `Missing Python package: ${moduleName}\n\n` +
                    `Install with: pip install ${this.getInstallPackageName(moduleName)}\n\n` +
                    `Full error: ${errorMessage}`
                );
            }
            
            throw new Error(`Python script failed: ${errorMessage}`);
        }
    }

    private static getInstallPackageName(moduleName: string): string {
        const packageMap: { [key: string]: string } = {
            'h5py': 'h5py',
            'numpy': 'numpy',
            'pandas': 'pandas',
            'pyarrow': 'pyarrow',
            'msgpack': 'msgpack',
            'joblib': 'joblib',
            'tables': 'tables'
        };
        
        return packageMap[moduleName] || moduleName;
    }

    static async runInlineScript(script: string): Promise<string> {
        const python = await this.findPython();
        
        try {
            const { stdout, stderr } = await execAsync(`${python} -c "${script.replace(/"/g, '\\"')}"`, {
                maxBuffer: 50 * 1024 * 1024,
                timeout: 30000
            });
            
            if (stderr && !stderr.includes('Warning')) {
                console.error('Python stderr:', stderr);
            }
            
            return stdout;
        } catch (error: any) {
            throw new Error(`Python script failed: ${error.stderr || error.message}`);
        }
    }
}
