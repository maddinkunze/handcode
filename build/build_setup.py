import os, sys
from cx_Freeze import setup, Executable
from build_common import path_src, path_lib, path_icon
from build_common import buildname, buildversion, buildcpr, buildpath

# Dependencies are automatically detected, but it might need fine tuning.
path_main = os.path.join(path_src, "main.py")
packages = []
includes = ["handwriting", "tkwidgets"]
includefiles = [
    (os.path.join(path_src, "data", "demo.txt"), os.path.join("data", "demo.txt")),
    (path_icon, os.path.join("lib", os.path.basename(path_icon)))
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
    'constants': [f"handcode_version=\"{buildversion}\""],
    'replace_paths': [("*", "")],
    'path': [*sys.path, path_src, path_lib],
}
bdist_mac_options = {
    'iconfile': path_icon,
    'bundle_name': buildpath,
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="HandCode",
    version=buildversion,
    description="HandCode: Handwriting GCode Generator",
    options={"build_exe": build_exe_options, "bdist_mac": bdist_mac_options},
    executables=[Executable(path_main, base=base, icon=path_icon, target_name=buildname, copyright=buildcpr)],
)
