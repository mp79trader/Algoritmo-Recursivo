const { app, BrowserWindow, screen } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

// Determine if we are in development mode
const isDev = process.env.NODE_ENV === 'development';

// Path to Python backend
const backendPath = isDev
  ? path.resolve(__dirname, '../../backend/main.py')
  : path.join(process.resourcesPath, 'backend/main.py');

// Path to Python interpreter
const getPythonPath = () => {
  if (isDev) {
    const rootDir = path.resolve(__dirname, '../../');
    // Check .venv
    let venvPath = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
    const fs = require('fs');
    if (fs.existsSync(venvPath)) return venvPath;

    // Check venv
    venvPath = path.join(rootDir, 'venv', 'Scripts', 'python.exe');
    if (fs.existsSync(venvPath)) return venvPath;

    // Fallback to global python
    return 'python';
  }
  return path.join(process.resourcesPath, 'python', 'python.exe');
};

const pythonExe = getPythonPath();


function startPythonBackend() {
  console.log(`Starting backend from: ${backendPath} using ${pythonExe}`);

  try {
    const fs = require('fs');
    const path = require('path');

    // Crear directorio de logs si no existe
    const logsDir = path.join(__dirname, '../../logs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }

    // Archivos de log
    const logFile = path.join(logsDir, 'backend.log');
    const errorLogFile = path.join(logsDir, 'backend_error.log');

    // Abrir archivos de log
    const out = fs.openSync(logFile, 'a');
    const err = fs.openSync(errorLogFile, 'a');

    // Spawn Python process
    // SIEMPRE ocultar la ventana de terminal para no confundir al usuario
    pythonProcess = spawn(pythonExe, [backendPath], {
      windowsHide: true,  // SIEMPRE ocultar terminal
      stdio: ['ignore', out, err],  // Redirigir stdout y stderr a archivos
      detached: false
    });

    console.log(`Backend started with PID: ${pythonProcess.pid}`);
    console.log(`Logs: ${logFile}`);
    console.log(`Errors: ${errorLogFile}`);

    pythonProcess.on('error', (err) => {
      console.error('Failed to start backend:', err);
    });

    pythonProcess.on('close', (code) => {
      console.log(`Backend exited with code ${code}`);
      // Cerrar archivos de log
      try {
        fs.closeSync(out);
        fs.closeSync(err);
      } catch (e) {
        // Ignorar errores al cerrar
      }
    });
  } catch (error) {
    console.error('Critical error starting backend:', error);
  }
}


function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: width,
    height: height,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false, // For simple ipc, or use preload
      preload: path.join(__dirname, 'preload.cjs')
    },
    icon: path.join(__dirname, '../public/assets/QuantumFFT.png')
  });

  // In development, load the local dev server (Vite)
  // In production, load the built index.html
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173').catch(e => {
      console.error('Failed to load URL:', e);
      // Retry logic could go here
    });
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startPythonBackend();

  // Give backend a moment to start (or implement a health check)
  setTimeout(createWindow, 2000);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});
