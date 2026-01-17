# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(SPECPATH).parent

block_cipher = None

# Main application analysis
a = Analysis(
    ['app/main.py'],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        # Include assets directory
        (str(ROOT_DIR / 'assets'), 'assets'),
        # Include styles directory
        (str(ROOT_DIR / 'styles'), 'styles'),
        # Include converter directory
        (str(ROOT_DIR / 'converter'), 'converter'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.scripts.pyside_tool',
        'reportlab',
        'PyPDF2',
        'tqdm',
        'progress',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Dataminer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # macOS specific
    icon=str(ROOT_DIR / 'assets' / 'icon.icns') if (ROOT_DIR / 'assets' / 'icon.icns').exists() else None,
    bundle_identifier='com.unit404.dataminer',
    info_plist={
        'CFBundleName': 'Dataminer',
        'CFBundleDisplayName': 'Dataminer',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.unit404.dataminer',
        'NSHighResolutionCapable': True,
        'LSApplicationCategoryType': 'public.app-category.utilities',
    }
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Dataminer.app',
        icon=str(ROOT_DIR / 'assets' / 'icon.icns') if (ROOT_DIR / 'assets' / 'icon.icns').exists() else None,
        bundle_identifier='com.unit404.dataminer',
        info_plist={
            'CFBundleName': 'Dataminer',
            'CFBundleDisplayName': 'Dataminer',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleIdentifier': 'com.unit404.dataminer',
            'NSHighResolutionCapable': True,
            'LSApplicationCategoryType': 'public.app-category.utilities',
        }
    )
