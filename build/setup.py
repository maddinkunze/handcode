import os, sys
from cx_Freeze import setup, Executable

path_src = os.path.join("..", "src")

# Dependencies are automatically detected, but it might need fine tuning.
packages = ["matplotlib", "tensorflow", "tensorflow_probability"]
includes = []
includefiles = [(os.path.join(path_src, "data", "demo.txt"), os.path.join("data", "demo.txt")), (os.path.join(path_src, "lib", "svg2gcode"), os.path.join("lib", "svg2gcode")), (os.path.join(path_src, "lib", "icon.ico"), os.path.join("lib", "icon.ico"))]
excludes = ["cachetools", "contourpy", "curses", "fontTools", "google_auth_oauthlib", "grpc", "h5py", "lib2to3", "markdown", "markupsafe", "oauthlib", "pasta", "pkg_ressources", "pyasn1", "pyasn1_modules", "pydoc_data", "pytz", "requests_oauthlib", "rsa", "setuptools", "tensorboard_data_server", "tensorflow_estimator", "tensorflow_io_gcs_filesystem", "test", "werkzeug", "wheel", "wsgiref", "xmlrpc", "zoneinfo"]
#excludes = []
optimization = 1
buildversion = "0.3.0"
buildpath = os.path.join("dist", "handcode-win64")
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

"""
My try at using optimization=2 (-00); did not really work yet
def insertline(filename, conditions, fillline):
    def checkcondition(condition, line):
        if (condition[0][0] == "="):
            return line == condition[1]
        if (condition[0][0] == "s"):
            return line.strip().startswith(condition[1])
        if (condition[0][0] == "e"):
            return line.strip().endswith(condition[1])
        return False
    def isskipcondition(condition):
        if len(condition[0]) < 2:
            return False
        if condition[0][-1] != "/":
            return False
        return True

    with open(filename, "r") as f:
        contents = f.readlines()

    state = 0
    for index, line in enumerate(contents):
        if (state < len(conditions)) and checkcondition(conditions[state], line):
            state += 1
            if (isskipcondition(conditions[state-1])):
                continue

        if (state == len(conditions)):
            if line == fillline:
                state = -1
            break

    if (state == len(conditions)):
        contents.insert(index, fillline)
        _cont = input(f"[WARNING] Optimization set to 2, this will insert a line into {filename}! Enter Y to continue: ")
        if _cont not in ["y", "Y"]:
            print(f"Did not override {filename}! The program might not work due to a docstring error. You can avoid this by setting the optimization variable in build.py to 0 or 1 or by allowing the change.")
            state = -1

    if (state == len(conditions)):
        with open(filename, "w") as f:
            f.write("".join(contents))

if optimization == 2:
    import numpy.core.overrides as _npor
    _nporfill = "    if dispatcher.__doc__ is None: dispatcher.__doc__ = ''\n"
    insertline(_npor.__file__, [("s", "def array_function_dispatch("), ("e/", ":"), ("s/", '"""'), ("e/", '"""')], _nporfill)

    import tensorflow
    _tfau = os.path.join(os.path.dirname(tensorflow.__file__), "python", "util", "all_util.py")
    _tfaufill = "    if doc_module.__doc__ is None: doc_module.__doc__ = ''\n"
    insertline(_tfau, [("s", "def make_all("), ("e/", ":"), ("s/", "for doc_module in")], _tfaufill)
    
"""

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
