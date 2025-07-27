import os
import sys

# Whether we are running in a frozen environment (i.e. cx_Freeze)
is_frozen = getattr(sys, "frozen", False)

# Runtime environment (i.e. operating system)
environment = None
if sys.platform == "win32":
    environment = "windows"
elif sys.platform == "darwin":
    environment = "macos"
elif sys.platform.startswith("linux"):
    environment = "linux"

# Tyoe of package (if applicable, e.g. "windows-exe", "linux-appimage", "macos-app")
package = None
if is_frozen:
    from BUILD_CONSTANTS import package  # type: ignore[import-not-found]

# Path of the directory with the main executable
path_exe_dir = os.path.dirname(os.path.realpath(sys.executable if is_frozen else __file__))

# Whether we have to assume that the built-in data directory is read-only
is_readonly = os.access(path_exe_dir, os.W_OK) is False

# Paths to where the output data and settings are stored by default
path_data = os.path.join(path_exe_dir, "data")
path_settings = os.path.join(path_data, "settings.json")

if is_readonly or package in ("linux-appimage", "macos-app"):
    _path_home = os.path.expanduser("~")
    if environment in ("macos", "linux"):
        path_data = os.path.join(_path_home, ".handcode")
    elif environment == "windows":
        path_data = os.path.join(_path_home, "AppData", "Local", "handcode")
    else:
        path_data = os.path.join(_path_home, "handcode")

    try:
        os.makedirs(path_data, exist_ok=True)
        import shutil
        path_settings = shutil.copy(path_settings, path_data)
    except:
        pass

# Path to the directory containing the libraries
path_lib = os.path.join(path_exe_dir, "lib")

path_icon = None
if environment == "windows":
    path_icon = os.path.join(path_lib, "icon.ico")
#elif package == "appimage":
#    pass
else:
    _path_icon_dir = path_exe_dir if is_frozen else path_lib
    path_icon = os.path.join(_path_icon_dir, "icon.png")

class CompressionConfig:
    def __init__(self, files: list[tuple[str, ...]] = [], ext: str = "bz2", depth: int = 3):
        self.ext = f"{os.path.extsep}{ext}"
        self.depth = depth
        self.files = files

_compression_files = [
    ("lib", "numpy"),
    ("lib", "tensorflow"),
]
_compression_default = None if is_readonly else CompressionConfig(_compression_files)
_compression_windows = CompressionConfig([
    *_compression_files,
    ("lib", "torch", "lib", "torch_cpu.dll"),
    ("lib", "torch", "lib", "torch_python.dll"),
])
_compression_macos = CompressionConfig([
    *_compression_files,
    ("lib", "libtorch.dylib"),
    ("lib", "libtorch_cpu.dylib"),
    ("lib", "libtorch_python.dylib"),
    ("lib", "libgfortran.5.dylib"),
])

# Lookup table for which packages can use compression
compression_lookup = {
    "linux-appimage": None,
    "macos-app": _compression_macos,
    "windows-exe": _compression_windows,
}

# Determine the actual compression configuration for the current runtime
compression: CompressionConfig | None = None
if is_frozen:
    compression = compression_lookup.get(package, _compression_default)

# HandCode version (declare here manally, if it cannot be determined automatically)
version_handcode = None
if is_frozen:
    # frozen builds will not contain the pyproject.toml file, but we will pass the version to cx_freeze as a build constant
    from BUILD_CONSTANTS import version_handcode # type: ignore[import-not-found]
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
assert isinstance(version_handcode, str), "Could not determine program version, please specify it manually in common.py"

# Add the library path to the system path (unless frozen, in which case it is already included)
if not is_frozen:
    sys.path.append(path_lib) # for clean build reasons we dont include lib.* (e.g. lib.handwriting)

import tkinter as tk
def set_tk_icon(root: tk.Tk):
    if environment == "windows":
        root.iconbitmap(path_icon)
    else:
        try:
            img = tk.PhotoImage(file=path_icon)
            root.iconphoto(True, img)
        except Exception as e:
            print(f"Warning: Could not set icon for tkinter window: {e}")
            pass
