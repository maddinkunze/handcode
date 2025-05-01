import os, sys
from cx_Freeze import setup, Executable

path_src = os.path.join("..", "src")
path_lib = os.path.join(path_src, "lib")
path_icon = os.path.join(path_lib, "icon.ico")

# Metadata
buildname = "HandCode"
buildversion = "0.4.2"
buildcpr = "© Martin Kunze - https://github.com/maddinkunze/handcode"
buildpath = os.path.join("dist", f"handcode-win64")

# Dependencies are automatically detected, but it might need fine tuning.
path_main = os.path.join(path_src, "main.py")
packages = []
includes = ["handwriting", "tkwidgets"]
includefiles = [
    (os.path.join(path_src, "data", "demo.txt"), os.path.join("data", "demo.txt")),
    (path_icon, os.path.join("lib", "icon.ico"))
]
excludes = []
optimization = 1
build_exe_options = {
    'build_exe': buildpath,
    'packages': packages,
    'includes': includes,
    'include_files': includefiles,
    'include_msvcr': True,
    'excludes': excludes,
    'optimize': optimization,
    'replace_paths': [("*", "")],
    'path': [*sys.path, path_src, path_lib],
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

if os.path.exists(buildpath + f"-v{buildversion}.zip"):
    print("/-----------------------------------------------------------------\\")
    print("| WARNING! There already exists a build with this version number! |")
    print("\\-----------------------------------------------------------------/")
    print()

setup(
    name="HandCode",
    version=buildversion,
    description="HandCode: Handwriting GCode Generator",
    options={"build_exe": build_exe_options},
    executables=[Executable(path_main, base=base, icon=path_icon, target_name=buildname, copyright=buildcpr)],
)
