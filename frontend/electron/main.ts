import { app, BrowserWindow } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import { spawn, ChildProcess } from 'node:child_process'
import http from 'node:http'

// ─── Debug Logging to File ───────────────────────────────────────────────────

const logDir = path.join(process.env.APPDATA || app.getPath('userData'), 'DesalPredictionApp')
try { fs.mkdirSync(logDir, { recursive: true }) } catch {}
const logFile = path.join(logDir, 'backend.log')
const logStream = fs.createWriteStream(logFile, { flags: 'w' })

function log(msg: string): void {
  const line = `[${new Date().toISOString()}] ${msg}`
  console.log(line)
  logStream.write(line + '\n')
}

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main.js
// │ │ └── preload.mjs
// │
process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let win: BrowserWindow | null
let backendProcess: ChildProcess | null = null

// ─── Backend Server Management ───────────────────────────────────────────────

function getBackendPath(): string {
  if (app.isPackaged) {
    // In production: backend is in extraResources
    return path.join(process.resourcesPath, 'backend_server', 'backend_server.exe')
  }
  // In development: use the PyInstaller dist output or run directly
  return path.join(__dirname, '..', '..', 'backend', 'dist', 'backend_server', 'backend_server.exe')
}

function startBackend(): void {
  const backendPath = getBackendPath()
  const backendExists = fs.existsSync(backendPath)
  log(`[Backend] Path: ${backendPath}`)
  log(`[Backend] Exists: ${backendExists}`)
  log(`[Backend] resourcesPath: ${process.resourcesPath}`)
  log(`[Backend] isPackaged: ${app.isPackaged}`)

  try {
    backendProcess = spawn(backendPath, [], {
      stdio: ['pipe', 'pipe', 'pipe'],
      detached: false,
      windowsHide: true,
    })

    backendProcess.stdout?.on('data', (data: Buffer) => {
      log(`[Backend stdout] ${data.toString().trim()}`)
    })

    backendProcess.stderr?.on('data', (data: Buffer) => {
      log(`[Backend stderr] ${data.toString().trim()}`)
    })

    backendProcess.on('error', (err: Error) => {
      log(`[Backend] Failed to start: ${err.message}`)
    })

    backendProcess.on('exit', (code: number | null) => {
      log(`[Backend] Exited with code ${code}`)
      backendProcess = null
    })
  } catch (err) {
    log(`[Backend] Error spawning process: ${err}`)
  }
}

function stopBackend(): void {
  if (backendProcess && !backendProcess.killed) {
    log('[Backend] Stopping...')
    try {
      // On Windows, we need taskkill for the process tree
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', String(backendProcess.pid), '/f', '/t'], {
          windowsHide: true,
        })
      } else {
        backendProcess.kill('SIGTERM')
      }
    } catch (err) {
      log(`[Backend] Error stopping: ${err}`)
    }
    backendProcess = null
  }
}

function waitForBackend(url: string, maxRetries = 30, interval = 1000): Promise<void> {
  return new Promise((resolve, reject) => {
    let attempts = 0

    const check = () => {
      attempts++
      log(`[Backend] Health check attempt ${attempts}/${maxRetries}...`)

      const req = http.get(url, (res) => {
        if (res.statusCode === 200) {
          log('[Backend] Server is ready!')
          resolve()
        } else {
          retry()
        }
      })

      req.on('error', () => {
        retry()
      })

      req.setTimeout(2000, () => {
        req.destroy()
        retry()
      })
    }

    const retry = () => {
      if (attempts >= maxRetries) {
        reject(new Error('[Backend] Server failed to start after maximum retries'))
      } else {
        setTimeout(check, interval)
      }
    }

    check()
  })
}

// ─── Window Creation ─────────────────────────────────────────────────────────

function createWindow() {
  win = new BrowserWindow({
    width: 1280,
    height: 800,
    icon: path.join(process.env.VITE_PUBLIC, 'electron-vite.svg'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
    },
    show: false, // Don't show until backend is ready
  })

  // Test active push message to Renderer-process.
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    // win.loadFile('dist/index.html')
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }

  win.once('ready-to-show', () => {
    win?.show()
    // Open DevTools for debugging:
    // win?.webContents.openDevTools()
  })
}

// ─── App Lifecycle ───────────────────────────────────────────────────────────

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.on('before-quit', () => {
  stopBackend()
})

app.whenReady().then(async () => {
  // Start the backend server
  startBackend()

  try {
    // Wait for the backend to become healthy
    await waitForBackend('http://127.0.0.1:8000/docs')
    log('[App] Backend is ready, creating window...')
  } catch (err) {
    log(`[App] Backend failed to start: ${err}`)
    // Still create window — it will show connection error in the UI
  }

  createWindow()
})
