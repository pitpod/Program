# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['program_main.py'],
    pathex=[],
    binaries=[],
    datas=[('image', 'image'), ('config.ini', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
a.datas += [('./image/hr.png', './image/hr.png', 'DATA')]
a.datas += [('./image/yuyu_logo.png', './image/yuyu_logo.png', 'DATA')]
a.datas += [('./config.ini', './config.ini', 'TEXT')]
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='契約日数チェック',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='image/hr.png',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='契約日数チェック',
)
