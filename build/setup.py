import os, sys
import pkg_resources
from cx_Freeze import setup, Executable

path_src = os.path.join("..", "src")

# Dependencies are automatically detected, but it might need fine tuning.
packages = ["tensorflow", "tensorflow_probability"]
includes = ["handwriting"]
includefiles = [(os.path.join(path_src, "data", "demo.txt"), os.path.join("data", "demo.txt")), (os.path.join(path_src, "lib", "icon.ico"), os.path.join("lib", "icon.ico"))]
excludes = ["cachetools", "contourpy", "curses", "fontTools", "google_auth_oauthlib", "grpc", "h5py", "lib2to3", "markdown", "markupsafe", "matplotlib", "oauthlib", "pasta", "pkg_ressources", "pyasn1", "pyasn1_modules", "pydoc_data", "pytz", "requests_oauthlib", "rsa", "scipy", "setuptools", "tensorboard_data_server", "tensorflow_estimator", "tensorflow_io_gcs_filesystem", "test", "werkzeug", "wheel", "wsgiref", "xmlrpc", "zoneinfo"]
optimization = 1
buildversion = "0.4.1"
buildpath = os.path.join("dist", f"handcode-win64")
build_exe_options = {
    'build_exe': buildpath,
    'packages': packages,
    'includes': includes,
    'include_files': includefiles,
    'include_msvcr': True,
    'excludes': excludes,
    'optimize': optimization,
    'replace_paths': [("*", "")],
    'path': [*sys.path, path_src, os.path.join(path_src, "lib"), os.path.join(path_src, "lib", "handwriting")],
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
    executables=[Executable(os.path.join(path_src, "main.py"), base=base, icon=os.path.join(path_src, "lib", "icon.ico"), target_name="HandCode", copyright="© Martin Kunze - https://github.com/maddinkunze/handcode")],
)
