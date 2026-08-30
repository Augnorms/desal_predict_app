# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Paths
app_dir = os.path.join('.', 'app')
models_dir = os.path.join(app_dir, 'models', 'saved_models')

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Bundle ML model files
        (os.path.join(models_dir, 'permeate_flowrate_model_rf.pkl'), os.path.join('app', 'models', 'saved_models')),
        (os.path.join(models_dir, 'permeate_flowtds_model_rf.pkl'), os.path.join('app', 'models', 'saved_models')),
    ],
    hiddenimports=[
        # FastAPI and dependencies
        'fastapi',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'starlette',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.responses',
        'starlette.routing',
        'starlette.websockets',
        # Uvicorn
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # Pydantic
        'pydantic',
        'pydantic_core',
        'annotated_types',
        # ML / Data
        'sklearn',
        'sklearn.ensemble',
        'sklearn.ensemble._forest',
        'sklearn.tree',
        'sklearn.tree._classes',
        'sklearn.utils._typedefs',
        'sklearn.neighbors._partition_nodes',
        'joblib',
        'pandas',
        'numpy',
        'scipy',
        # App modules
        'app',
        'app.main',
        'app.predict',
        'app.database',
        'app.iot_generator',
        'app.validate_input',
        'app.validate_input.manual_data',
        # Other
        'multiprocessing',
        'sqlite3',
        'asyncio',
        'typing',
        'typing_extensions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='backend_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console for backend server logging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='backend_server',
)
