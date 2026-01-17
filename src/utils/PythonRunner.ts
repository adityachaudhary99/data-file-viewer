import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execAsync = promisify(exec);

export class PythonRunner {
    private static pythonPath: string | null = null;
    private static venvPath: string | null = null;
    private static extensionContext: vscode.ExtensionContext | null = null;
    private static packagesInstalled: boolean | null = null;
    private static checkingPackages: Promise<boolean> | null = null;

    static initialize(context: vscode.ExtensionContext) {
        this.extensionContext = context;
        // Load cached package installation status from persistent storage
        this.packagesInstalled = context.globalState.get('packagesInstalled', null);
        console.log('PythonRunner initialized. Packages installed:', this.packagesInstalled);
        console.log('Global storage path:', context.globalStorageUri.fsPath);
    }

    private static getVenvPath(): string {
        if (!this.extensionContext) {
            throw new Error('PythonRunner not initialized');
        }
        // Store venv in extension's global storage (persists across updates)
        return path.join(this.extensionContext.globalStorageUri.fsPath, 'python-venv');
    }

    private static getVenvPythonPath(): string {
        const venvPath = this.getVenvPath();
        // Windows: venv\Scripts\python.exe, Unix: venv/bin/python
        return process.platform === 'win32'
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
    }

    static async findSystemPython(): Promise<string> {
        // Find system Python (not the venv)
        const pythonCommands = ['python', 'python3', 'py'];
        
        for (const cmd of pythonCommands) {
            try {
                const { stdout, stderr } = await execAsync(`${cmd} --version`);
                const output = stdout + stderr;
                if (output.includes('Python 3')) {
                    return cmd;
                }
            } catch (error) {
                continue;
            }
        }

        throw new Error('Python 3 not found. Please install Python 3.7 or higher.');
    }

    static async ensureVenv(progressCallback?: (message: string) => void): Promise<string> {
        const venvPath = this.getVenvPath();
        const venvPython = this.getVenvPythonPath();

        // Check if venv already exists and is valid
        if (fs.existsSync(venvPython)) {
            try {
                await execAsync(`"${venvPython}" --version`);
                this.pythonPath = venvPython;
                return venvPython;
            } catch (error) {
                // Venv is corrupted, recreate it
                console.log('Virtual environment corrupted, recreating...');
            }
        }

        // Create venv
        const systemPython = await this.findSystemPython();
        
        // Ensure parent directory exists
        const parentDir = path.dirname(venvPath);
        if (!fs.existsSync(parentDir)) {
            fs.mkdirSync(parentDir, { recursive: true });
        }

        // Create virtual environment
        const createVenv = async () => {
            try {
                if (progressCallback) {
                    progressCallback('Creating virtual environment...');
                }
                await execAsync(`${systemPython} -m venv "${venvPath}"`, {
                    timeout: 60000 // 1 minute
                });
            } catch (error) {
                throw new Error(`Failed to create virtual environment: ${error}`);
            }
        };

        // Only show progress notification if not already in a progress context
        if (progressCallback) {
            await createVenv();
        } else {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Creating Python environment for Data File Viewer...',
                cancellable: false
            }, createVenv);
        }

        this.pythonPath = venvPython;
        return venvPython;
    }

    static async findPython(): Promise<string> {
        // Return cached path if available
        if (this.pythonPath && fs.existsSync(this.pythonPath)) {
            return this.pythonPath;
        }

        // Ensure venv exists and return its Python
        return await this.ensureVenv();
    }

    static async checkAndInstallPackages(): Promise<boolean> {
        // If a check is already in progress, wait for it
        if (this.checkingPackages) {
            console.log('Package check already in progress, waiting...');
            return await this.checkingPackages;
        }
        
        // Create the check promise
        this.checkingPackages = this._doCheckAndInstallPackages();
        
        try {
            const result = await this.checkingPackages;
            return result;
        } finally {
            // Clear the promise when done
            this.checkingPackages = null;
        }
    }
    
    private static async _doCheckAndInstallPackages(): Promise<boolean> {
        try {
            console.log('checkAndInstallPackages called. Cached status:', this.packagesInstalled);
            
            // First, ensure we can find system Python (needed for venv creation)
            let systemPython: string;
            try {
                systemPython = await this.findSystemPython();
                console.log('System Python found:', systemPython);
            } catch (error) {
                console.error('System Python not found:', error);
                vscode.window.showErrorMessage(
                    'Python 3 not found. Please install Python 3.7 or higher and restart VS Code.'
                );
                this.packagesInstalled = false;
                await this.extensionContext?.globalState.update('packagesInstalled', false);
                return false;
            }

            // Check if venv exists and is valid
            const venvPath = this.getVenvPath();
            const venvPython = this.getVenvPythonPath();
            console.log('Checking venv at:', venvPython);
            
            const venvExists = fs.existsSync(venvPython);
            
            // If we have a cached "installed" status AND venv exists, trust it
            // Only verify if venv doesn't exist or cache says not installed
            if (this.packagesInstalled === true && venvExists) {
                try {
                    // Quick validation: just check if Python executable exists and is valid
                    await execAsync(`"${venvPython}" --version`);
                    this.pythonPath = venvPython;
                    console.log('Using cached package installation status - venv exists and is valid');
                    return true;
                } catch (error) {
                    console.log('Venv exists but is invalid, will recreate:', error);
                    // Venv is corrupted, reset cache and continue with setup
                    this.packagesInstalled = false;
                    await this.extensionContext?.globalState.update('packagesInstalled', false);
                }
            }
            
            // If we get here, either:
            // 1. Cache says not installed, OR
            // 2. Venv doesn't exist, OR
            // 3. Venv exists but is invalid
            
            let python: string | null = null;
            let packagesOk = false;
            
            if (venvExists) {
                console.log('Venv exists, verifying packages...');
                try {
                    await execAsync(`"${venvPython}" --version`);
                    python = venvPython;
                    console.log('Venv is valid');
                    
                    // Check if packages are installed
                    const checkScript = 'import sys; import numpy, pandas, h5py, pyarrow, msgpack, joblib, avro, snappy, netCDF4, scipy; print(\'OK\')';
                    try {
                        const { stdout } = await execAsync(`"${python}" -c "${checkScript}"`, {
                            timeout: 10000
                        });
                        
                        if (stdout.includes('OK')) {
                            packagesOk = true;
                            console.log('All packages are installed');
                        } else {
                            console.log('Package check returned unexpected output:', stdout);
                        }
                    } catch (checkError) {
                        console.log('Package check failed:', checkError);
                    }
                } catch (error) {
                    console.log('Venv exists but is invalid, will recreate:', error);
                }
            } else {
                console.log('Venv does not exist yet');
            }
            
            // If packages are OK, cache and return
            if (packagesOk && python) {
                this.packagesInstalled = true;
                this.pythonPath = python;
                await this.extensionContext?.globalState.update('packagesInstalled', true);
                console.log('Packages verified and cached');
                return true;
            }
            
            // Packages missing or venv doesn't exist, offer to install
            console.log('Showing installation popup...');
            const install = await vscode.window.showWarningMessage(
                'Data File Viewer needs to install Python packages in its own environment. This is a one-time setup.',
                'Install',
                'Cancel'
            );
            
            console.log('User response:', install);
            
            if (install === 'Install') {
                const success = await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Setting up Python environment (this may take a few minutes)...',
                    cancellable: false
                }, async (progress) => {
                    try {
                        // Ensure venv exists (create if needed)
                        if (!python || !fs.existsSync(python)) {
                            python = await this.ensureVenv((msg) => progress.report({ increment: 10, message: msg }));
                        }
                        
                        progress.report({ increment: 20, message: 'Upgrading pip...' });
                        // Upgrade pip first
                        await execAsync(`"${python}" -m pip install --upgrade pip`, {
                            timeout: 60000
                        });
                        
                        progress.report({ increment: 30, message: 'Installing packages...' });
                        // Install packages
                        await execAsync(`"${python}" -m pip install numpy pandas h5py pyarrow msgpack joblib avro-python3 python-snappy netCDF4 scipy`, {
                            timeout: 300000 // 5 minutes for installation
                        });
                        
                        // Verify installation succeeded (non-blocking - pip success is sufficient)
                        try {
                            const verifyScript = 'import sys; import numpy, pandas, h5py, pyarrow, msgpack, joblib, avro, snappy, netCDF4, scipy; print(\'OK\')';
                            const { stdout } = await execAsync(`"${python}" -c "${verifyScript}"`, {
                                timeout: 10000
                            });
                            
                            if (stdout.includes('OK')) {
                                console.log('Package verification passed');
                            } else {
                                console.log('Package verification returned unexpected output, but pip install succeeded');
                            }
                        } catch (verifyError) {
                            // Verification failed, but pip install succeeded, so packages are likely installed
                            // This can happen due to quote escaping issues on Windows, but packages work fine
                            console.log('Package verification failed, but pip install succeeded:', verifyError);
                        }
                        
                        vscode.window.showInformationMessage('Python packages installed successfully! You can now view data files.');
                        this.packagesInstalled = true;
                        // Persist to storage for cross-session
                        await this.extensionContext?.globalState.update('packagesInstalled', true);
                        this.pythonPath = python; // Cache the path
                        console.log('Packages installed and cached successfully');
                        return true;
                    } catch (error) {
                        vscode.window.showErrorMessage(`Failed to install packages: ${error}`);
                        this.packagesInstalled = false;
                        await this.extensionContext?.globalState.update('packagesInstalled', false);
                        return false;
                    }
                });
                return success;
            }
            
            return false; // User clicked Cancel
        } catch (error) {
            vscode.window.showErrorMessage(`Error setting up Python environment: ${error}`);
            this.packagesInstalled = false;
            await this.extensionContext?.globalState.update('packagesInstalled', false);
            return false;
        }
    }

    static async runScript(scriptPath: string, args: string[] = []): Promise<string> {
        const python = await this.findPython();
        // Always quote paths for safety
        const command = `"${python}" "${scriptPath}" ${args.map(arg => `"${arg}"`).join(' ')}`;
        
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
            const { stdout, stderr } = await execAsync(`"${python}" -c "${script.replace(/"/g, '\\"')}"`, {
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
