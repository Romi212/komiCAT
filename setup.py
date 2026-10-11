# setup.py
from cx_Freeze import setup, Executable

setup(
    name="KomiCAT",
    version="1.0.0",
    options={
        "build_exe": {
            "packages": ["torch", "PyQt6", "jamdict", "manga_ocr", "ultralytics"],
            "include_files": [],        # no models here, they download on first run
        },
        "bdist_msi": {
            "upgrade_code": "{PUT-A-FIXED-GUID-HERE}",   # keep the same across versions
            "add_to_path": False,
        },
    },
    executables=[Executable("src/main.py", base="gui", target_name="KomiCAT.exe",
                            shortcut_name="KomiCAT", shortcut_dir="DesktopFolder")],
)