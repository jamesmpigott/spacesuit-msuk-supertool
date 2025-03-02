# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui.py'],
    pathex=['/usr/local/lib', '/opt/homebrew/lib'],
    binaries=[],
    datas=[('assets/*', 'assets')],
    hiddenimports=['libxmp'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hooks/init_libxmp.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Spacesuit-MSUK-SuperTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/favicon.ico',
)

app = BUNDLE(
    exe,
    name='Spacesuit-MSUK-SuperTool.app',
    icon='assets/favicon.ico',
)
