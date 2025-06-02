import os
import sys
import bz2
import shutil
import typing
from cx_Freeze import build_exe
from build_common import use_compression, ext_compression, files_compressed, compression_depth


# ---------------------------------------------------
# Declaring paths to remove and/or optimize otherwise
# ---------------------------------------------------

move_files = [
    (("frozen_application_license.txt",), ("lib", "cxfreeze_license.txt")),
]
remove_files = [
    ("_asyncio.pyd",),
    ("_bz2.pyd",),
    ("_decimal.pyd",),
    ("_elementtree.pyd",),
    ("_hashlib.pyd",),
    ("_queue.pyd",),
    ("_ssl.pyd",),
    ("_testbuffer.pyd",),
    ("_uuid.pyd",),
    ("pyexpat.pyd",),
]
remove_dirs = [
    ("lib", "numpy", "testing"),
    ("lib", "distutils", "command"),
    ("lib", "distutils", "tests"),
    ("lib", "handwriting", "logs"),
    ("lib", "numpy", "_pyinstaller"),
    ("lib", "numpy", "core", "include"),
    ("lib", "numpy", "core", "lib"),
    ("lib", "numpy", "array_api", "tests"),
    ("lib", "numpy", "distutils"),
    ("lib", "numpy", "doc"),
    ("lib", "numpy", "f2py"),
    ("lib", "numpy", "random", "lib"),
    ("lib", "numpy", "testing", "tests"),
    ("lib", "dateutil", "zoneinfo"),
    ("lib", "pytz", "zoneinfo"),
    ("lib", "tensorboard",),
    ("lib", "google", "_upb"),
    ("lib", "google", "auth"),
    ("lib", "google", "oauth"),
    ("lib", "importlib", "metadata"),
    ("lib", "tcl8",),
    ("lib", "tcl8.6", "encoding"),
    ("lib", "tcl8.6", "http1.0"),
    ("lib", "tcl8.6", "msgs"),
    ("lib", "tcl8.6", "opt0.4"),
    ("lib", "tcl8.6", "tzdata"),
    ("lib", "tk8.6", "demos"),
    ("lib", "tk8.6", "images"),
    ("lib", "tk8.6", "msgs"),
    ("lib", "tkinter", "test"),
    ("lib", "tensorflow", "include"),
    ("lib", "tensorflow", "xla_aot_runtime_src"),
    ("lib", "pkg_ressources",),
    ("lib", "html",),
    ("lib", "google", "oauth2"),
    ("lib", "PIL",),
    ("lib", "pyparsing",),
    ("lib", "requests", "packages"),
]
remove_files_pattern: list[tuple[tuple[str, ...], "_rfilterf"]] = [
    (("lib", "numpy"), lambda _, f: f.endswith("pyi") or f.endswith("pxd")),
]


# -------------------------------------------------------
# Declaring platform-specific files to remove or compress
# -------------------------------------------------------

if sys.platform == "darwin":
    remove_files.append(("lib", "torch", "bin", "protoc"))
    remove_files.append(("lib", "torch", "bin", "protoc-3.13.0.0"))
    remove_files.append(("lib", "torch", "lib", "libtorch.dylib"))
    remove_files.append(("lib", "torch", "lib", "libtorch_cpu.dylib"))
    remove_files.append(("lib", "torch", "lib", "libtorch_python.dylib"))
    remove_files.append(("lib", "numpy", ".dylibs", "libgfortran.5.dylib"))
    remove_files.append(("lib", "libcrypto.1.1.dylib"))
    remove_files.append(("lib", "libssl.1.1.dylib"))
else:
    remove_dirs.append(("lib", "ctypes", "macholib"))

if sys.platform == "win32":
    remove_files.append(("lib", "libcrypto-3.dll",)),
    remove_files.append(("lib", "libssl-3.dll",)),
    remove_files.append(("lib", "numpy", "core", "_simd.cp311-win_amd64.pyd")),
    move_files.append((("vcruntime140.dll",), ("lib", "vcruntime140.dll")))
    move_files.append((("vcruntime140_1.dll",), ("lib", "vcruntime140_1.dll")))


# --------------------------------------
# Actual functions to optimize the build
# --------------------------------------

def move_build_files(build_path: str):
    for path, target in move_files:
        path_from = os.path.join(build_path, *path)
        path_to = os.path.join(build_path, *target)
        print(f"Moving {path_from} to {path_to}")
        os.rename(path_from, path_to)

_rfilterf = typing.Callable[[str, str], bool]
def remove_files_template(build_path: str):
    for path, template in remove_files_pattern:
        _remove_files_template(os.path.join(build_path, *path), template)

def _remove_files_template(path: str, filterf: _rfilterf):
    for item in os.listdir(path):
        path_item = os.path.join(path, item)

        if os.path.isdir(path_item):
            _remove_files_template(path_item, filterf)
            continue

        if os.path.isfile(path_item) and filterf(path, item):
            os.remove(path_item)

def remove_unnecessary_files(build_path: str):
    for path in remove_files:
        path_full = os.path.join(build_path, *path)
        if not os.path.isfile(path_full):
            continue

        print(f"Removing {path_full}")
        os.remove(path_full)

def remove_unnecessary_dirs(build_path: str):
    for path in remove_dirs:
        path_full = os.path.join(build_path, *path)
        if not os.path.isdir(path_full):
            continue

        print(f"Removing directory {path_full}")
        shutil.rmtree(path_full, ignore_errors=True)

def compress_large_files(build_path: str):
    for path in files_compressed:
        path_full = os.path.join(build_path, *path)
        if os.path.isdir(path_full):
            print(f"Compressing files in {path_full}")
            _compress_large_files(path_full, 500_000, 0.6, [], compression_depth)
        elif os.path.isfile(path_full):
            _compress_large_file(path_full, 500_000, 0.6)

def _compress_large_files(basedir, minsize, compressfactor, excludes, maxlevel):
    if maxlevel < 0:
        return
    
    for item in os.listdir(basedir):
        path_item = os.path.join(basedir, item)
        if (item in excludes) or (path_item in excludes):
            continue
        
        if os.path.isdir(path_item):
            _compress_large_files(path_item, minsize, compressfactor, excludes, maxlevel-1)
        elif os.path.isfile(path_item):
            _compress_large_file(path_item, minsize, compressfactor)

def _compress_large_file(path: str, minsize: int, compressfactor: float):
    filesize_orig = os.stat(path).st_size
    if filesize_orig < minsize:
        return
    path_compressed = path + ext_compression

    print(f"Compressing {path}({ext_compression})", end="")
    file_orig = open(path, "rb")
    file_compressed = bz2.open(path_compressed, "wb")
    file_compressed.write(file_orig.read())
    file_compressed.close()
    file_orig.close()
    
    filesize_compressed = os.stat(path_compressed).st_size
    path_del = path
    if (filesize_compressed / filesize_orig) > compressfactor:
        print(f" (discarded)", end="")
        path_del = path_compressed
    os.remove(path_del)
    print()

def optimize_build(build_path: str):
    """
    Optimize the build by removing unnecessary files and directories.
    This is useful for reducing the size of the final distribution.
    """
    move_build_files(build_path)
    remove_unnecessary_dirs(build_path)
    remove_unnecessary_files(build_path)
    remove_files_template(build_path)
    if use_compression:
        compress_large_files(build_path)

# patch build_exe.run to allow us to remove files between build_exe and bdist_*
def patch_build_exe_run():
    """
    Patch the build_exe.run method to allow us to remove files and directories after the build is done.
    This is useful for removing unnecessary files that are not needed in the final distribution.
    """
    _old_build_exe_run = build_exe.run
    def _new_build_exe_run(self: build_exe):
        _old_build_exe_run(self)
        optimize_build(self.build_exe)        
    build_exe.run = _new_build_exe_run