# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['guitest.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        ('icons', 'icons'),
        ('C:/Users/AIBENJA/AppData/Local/Programs/Python/Python313/Lib/site-packages/rasterio/gdal_data', 'rasterio/gdal_data'),
        ('C:/Users/AIBENJA/AppData/Local/Programs/Python/Python313/Lib/site-packages/pyproj/proj_dir/share/proj', 'pyproj/share/proj'),
        ('C:/Users/AIBENJA/AppData/Local/Programs/Python/Python313/Lib/site-packages/pvevti/prefs.json', 'pvevti')
    ],
    hiddenimports=['rasterio.sample', 'requests', 'certifi', 'pvevti'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='File Processing Tool',
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
    icon='icon.ico',
    onefile=True
)
#coll = COLLECT(
#    exe,
#    a.binaries,
#    a.datas,
#    strip=False,
#    upx=True,
#    upx_exclude=[],
#    name='guitest',
#)
