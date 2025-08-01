import os, sys
from cx_Freeze import setup, Executable
from build_common import path_src, path_lib, path_icon
from build_common import buildname, buildversion, buildcpr
from build_config import buildpath, package_to_build, buildbase
from build_optimize import patch_build_exe_run

# Dependencies are automatically detected, but it might need fine tuning.
path_main = os.path.join(path_src, "main.py")
packages = []
includes = []
includefiles = [
    (os.path.join(path_src, "data", "demo.txt"), os.path.join("data", "demo.txt")),
]
if sys.platform == "win32":
    includefiles.append((path_icon, os.path.join("lib", "icon.ico")))
excludes = ["sqlite3", "networkx", "lib"]
bin_excludes = [
    "model.tflite",
    "model-17900.data-00000-of-00001",
    "model-17900.index",
    "model-17900.meta",
]
optimization = 1
build_exe_options = {
    'build_exe': buildpath,
    'packages': packages,
    'includes': includes,
    'include_files': includefiles,
    'include_msvcr': True,
    'excludes': excludes,
    'bin_excludes': bin_excludes,
    'optimize': optimization,
    'constants': [
        f"version_handcode=\"{buildversion}\"",
        f"package=\"{package_to_build}\"",
    ],
    'replace_paths': [("*", "")],
    'path': [*sys.path, path_src, path_lib],
}
bdist_mac_options = {
    'iconfile': path_icon,
    'bundle_name': buildpath,
}

patch_build_exe_run()

setup(
    name="HandCode",
    version=buildversion,
    description="HandCode: Handwriting GCode Generator",
    options={"build_exe": build_exe_options, "bdist_mac": bdist_mac_options},
    executables=[Executable(path_main, base=buildbase, icon=path_icon, target_name=buildname, copyright=buildcpr)],
)
