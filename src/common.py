import os
import sys

is_frozen = getattr(sys, "frozen", False)
path_exe_dir = os.path.dirname(os.path.realpath(sys.executable if is_frozen else __file__))
path_data = os.path.join(path_exe_dir, "data")
path_settings = os.path.join(path_data, "settings.json")
path_lib = os.path.join(path_exe_dir, "lib")
if sys.platform == "win32":
    path_icon = os.path.join(path_lib, "icon.ico")
else:
    _path_icon_dir = path_exe_dir if is_frozen else path_lib
    path_icon = os.path.join(_path_icon_dir, "icon.png")

use_compression = True
ext_compression = f"{os.extsep}bz2"
compression_depth = 3
files_compressed = [
    ("lib", "numpy"),
    ("lib", "tensorflow"),
]
if sys.platform == "darwin":
    files_compressed.append(("lib", "libtorch.dylib"))
    files_compressed.append(("lib", "libtorch_cpu.dylib"))
    files_compressed.append(("lib", "libtorch_python.dylib"))
    files_compressed.append(("lib", "libgfortran.5.dylib"))
if sys.platform == "win32":
    files_compressed.append(("lib", "torch", "lib", "torch_cpu.dll"))
    files_compressed.append(("lib", "torch", "lib", "torch_python.dll"))

version_handcode = None # specify handcode version here, if it cannot be determined automatically
if getattr(sys, "frozen", False):
    # frozen builds will not contain the pyproject.toml file, but we will pass the version to cx_freeze as a build constant
    from BUILD_CONSTANTS import handcode_version # type: ignore[import-not-found]
elif version_handcode is None:
    # for non-frozen builds, we can read the version from pyproject.toml
    import re
    re_version = re.compile(r"^version\s*=\s*['\"]([^'\"]+)['\"]\s*$", re.MULTILINE)
    path_pyproject = os.path.join(path_exe_dir, os.pardir, "pyproject.toml")
    assert os.path.exists(path_pyproject), "Could not determine program version because pyproject.toml was not found, please specify the version manually in common.py"
    with open(path_pyproject, "r", encoding="utf-8") as file_pyproject:
        match_version = re.search(re_version, file_pyproject.read())
    assert match_version is not None, "Could not determine program version from pyproject.toml, please specify it manually in common.py"
    version_handcode = match_version.group(1)
assert version_handcode is not None, "Could not determine program version, please specify it manually in common.py"

sys.path.append(path_lib) # for clean build reasons we dont include lib.handwriting

import tkinter as tk
def set_tk_icon(root: tk.Tk):
    if sys.platform == "win32":
        root.iconbitmap(path_icon)
    else:
        try:
            img = tk.PhotoImage(file=path_icon)
            root.iconphoto(True, img)
        except Exception:
            pass