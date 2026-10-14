# 🌊 Desalination Prediction & IoT Telemetry System

[![GitHub Release](https://img.shields.io/github/v/release/Augnorms/desal_predict_app?include_prereleases&color=blue&label=Latest%20Release)](https://github.com/Augnorms/desal_predict_app/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-brightgreen.svg)]()
[![Electron](https://img.shields.io/badge/Desktop-Electron-47848F?logo=electron&logoColor=white)]()
[![Vue 3](https://img.shields.io/badge/Frontend-Vue%203%20%7C%20Vite-4FC08D?logo=vuedotjs&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)]()
[![Python](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-F7931E?logo=scikitlearn&logoColor=white)]()

A modern desktop application for **Reverse Osmosis (RO) Desalination Plant Monitoring**, combining **Machine Learning models** for performance forecasting with a **real-time synthetic IoT telemetry stream**.

Packaged as a standalone Windows desktop app using **Electron**, **Vue 3**, **Tailwind CSS**, and an embedded **FastAPI / PyInstaller** service.

---

## 🚀 Quick Download

You can download the ready-to-use Windows installer directly from the releases page:

👉 **[Download Latest Windows Installer (.exe)](https://github.com/Augnorms/desal_predict_app/releases/latest)**

1. Download `Desalination Prediction App-Windows-x.x.x-Setup.exe`.
2. Run the installer and follow the setup wizard.
3. Launch **Desalination Prediction App** from your desktop or start menu.

---

## ✨ Features

- **🧠 Machine Learning Predictions**:
  - Predicts **Permeate Flowrate** ($m^3/h$) and **Permeate TDS** ($ppm$) using trained Random Forest models.
  - Computes water quality status: *Excellent*, *Good*, *Warning*, or *Poor*.
  - Input features: Feed Flowrate, Feed TDS, Feed Salinity, Temperature, Recovery rate, Flux, and Pressure Drop.

- **📡 Real-Time IoT Telemetry Stream**:
  - Live WebSocket stream simulating sensor telemetry from desalination plant equipment.
  - Real-time visualization of membrane performance metrics and operational stability.

- **📊 Data History & Logging**:
  - Local SQLite database logging operational entries and prediction history.
  - Easy review of past predictions and plant conditions.

- **🖥️ Standalone Desktop Experience**:
  - Electron-powered desktop application bundled with an embedded Python backend (no manual Python or Node.js runtime installation needed for end users).

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Electron Desktop App                 │
│                                                        │
│  ┌─────────────────────────┐  WebSocket / HTTP API    │
│  │     Vue 3 + Vite UI     │ ◄───────────────────────► │
│  │ (Tailwind CSS, Lucide)  │                           │
│  └─────────────────────────┘                           │
│               ▲                                        │
│               │ Spawns background process              │
│  ┌────────────┴────────────┐                           │
│  │  FastAPI Backend Server │                           │
│  │  • Scikit-learn Models  │                           │
│  │  • SQLite Storage       │                           │
│  │  • IoT Telemetry Stream │                           │
│  └─────────────────────────┘                           │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ Development & Local Setup

If you want to run or contribute to the project from source code:

### Prerequisites
- **Node.js**: v18+ & npm
- **Python**: 3.10+
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Augnorms/desal_predict_app.git
cd desalination_prediction_app
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install Python dependencies
pip install -r requirements.txt

# Run backend API server
python run.py
```
The FastAPI backend will start at `http://127.0.0.1:8000` with interactive API docs available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend

# Install Node dependencies
npm install

# Run Vite dev server with Electron
npm run dev
```

---

## 📦 Building the Standalone Installer

To build the complete standalone Windows installer executable (`.exe`):

```bash
cd frontend
npm run build
```

This single command will:
1. Compile the Python FastAPI backend into a standalone executable using **PyInstaller**.
2. Build the Vue 3 frontend with **Vite**.
3. Package everything into a Windows installer with **Electron Builder**.

The resulting setup file will be located at:
```
frontend/release/<version>/Desalination Prediction App-Windows-<version>-Setup.exe
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
