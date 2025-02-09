# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['install_deps.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/*', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=['assets/favicon.ico'],
)