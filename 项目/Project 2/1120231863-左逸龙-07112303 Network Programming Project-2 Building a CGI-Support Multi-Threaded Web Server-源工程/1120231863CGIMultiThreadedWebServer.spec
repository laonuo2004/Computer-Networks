# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import shutil
import stat


project_root = Path(SPECPATH)
package_root = Path(DISTPATH) / "1120231863CGIMultiThreadedWebServer"

# copytree preserves the Windows read-only attribute carried by some source
# directories.  Clear it before PyInstaller recreates an existing bundle so
# repeated clean builds work reliably.
if package_root.exists():
    for old_path in sorted(package_root.rglob("*"), reverse=True):
        old_path.chmod(stat.S_IWRITE)
    package_root.chmod(stat.S_IWRITE)
    shutil.rmtree(package_root)

a = Analysis(
    [str(project_root / "web_server.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "webroot"), "webroot"),
        (str(project_root / "packaging" / "README.txt"), "."),
    ],
    hiddenimports=["cgi_apps.calculator", "cgi_apps.query"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="1120231863CGIMultiThreadedWebServer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="1120231863CGIMultiThreadedWebServer",
)

# PyInstaller 6 places collected data inside ``_internal``.  The webroot is
# deliberately copied next to the executable because it contains mutable
# runtime data (SQLite and access logs) and is part of the submitted server
# directory layout.
shutil.copytree(project_root / "webroot", package_root / "webroot", dirs_exist_ok=True)
shutil.copy2(project_root / "packaging" / "README.txt", package_root / "README.txt")
