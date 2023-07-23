import sys, os
from cx_Freeze import setup, Executable

path_src = os.path.join("..", "src")

# Dependencies are automatically detected, but it might need fine tuning.
packages = ["matplotlib"]
includes = []
includefiles = [os.path.join(path_src, "data/"), os.path.join(path_src, "lib/")]
excludes = ["asnycio", "atomicwrites", "attr", "backcall", "bleach", "bs4", "certifi", "chardet", "cloudpickle", "curses", "Cython", "defusedxml", "grpc", "html", "h5py", "html5lib", "idna", "importlib_metadata", "iniconfig", "ipykernel", "IPython", "ipython_genutils", "jedi", "jinja2", "jsonschema", "jupyter_client", "jupyter_core", "lib2to3", "llvmlite", "lxml", "markdown", "markupsafe", "mock", "msilib", "nbconvert", "nbformat", "notebook", "numba", "packaging", "parso", "pkg_resources", "pluggy", "prompt_toolkit", "psutil", "py", "pydoc_data", "pygments", "pyreadline", "pyrsistent", "pytest", "pyximport", "setuptools", "simplejson", "soupsieve", "sqlite3", "test", "testpath", "toml", "tornado", "traitlets", "urllib3", "wcwidth", "werkzeug", "win32com", "wsgiref", "xmlrpc", "yaml", "zmq"]
optimization = 1
build_exe_options = {
    'build_exe': "dist/handcode-win64",
    'packages': packages,
    'includes': includes,
    'include_files': includefiles,
    'excludes': excludes,
    'optimize': optimization,
    'path': [*sys.path, path_src, os.path.join(path_src, "handwriting")], 
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

setup(
    name="HandCode",
    version="0.2.0",
    description="HandCode: Handwriting GCode Generator",
    options={"build_exe": build_exe_options},
    executables=[Executable(os.path.join(path_src, "main.py"), base=base, icon=os.path.join(path_src, "lib", "icon.ico"), target_name="HandCode")],
)
