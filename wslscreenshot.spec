# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[
        ('.venv/Library/bin/libexpat.dll', '.'),
        ('.venv/Library/bin/ffi.dll', '.'),
        ('.venv/Library/bin/ffi-7.dll', '.'),
        ('.venv/Library/bin/ffi-8.dll', '.'),
        ('.venv/Library/bin/liblzma.dll', '.'),
    ],
    datas=[
        ('config/config.json', 'config'),
        ('config/config.schema.json', 'config'),
    ],
    hiddenimports=[
        'win10toast',
        'pynput.keyboard',
        'pynput.mouse',
        'PIL._tkinter_finder',
        'xml.parsers.expat',
        'pyexpat',
        'xml.etree.ElementTree',
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
    name='WSLScreenshot',
    debug=False,  # Disable debug for release
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app - no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,  # Don't require admin by default
    icon=None,  # Add icon path here if you have one
)
