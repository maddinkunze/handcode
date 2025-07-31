import os
from build_common import CompressionConfig
from build_common import buildversion, path_src, path_assets, path_dist, environment, compression_lookup, _package_key, _remove_file_filter
from build_utils import to_zip_file

# Define default build configuration values
def pre_build_command(): ...
def post_exe_command(): ...
def post_build_command(): ...
buildbase: str|None = None
include_files = [
    (os.path.join(path_src, "data", "demo.txt"), os.path.join("data", "demo.txt")),
]
move_files: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
    (("frozen_application_license.txt",), ("lib", "cxfreeze_license.txt")),
]
remove_files: list[tuple[str, ...]] = [
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
remove_dirs: list[tuple[str, ...]] = [
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
remove_files_pattern: list[tuple[tuple[str, ...], _remove_file_filter]] = [
    (("lib", "numpy"), lambda _, f: f.endswith("pyi") or f.endswith("pxd")),
]
clean_dirs: list[str] = []
clean_files: list[str] = []
name_icon: str = "icon.png"


# Determine which package should be built
package_to_build = None

if _package_key in os.environ:
    package_to_build = os.environ[_package_key].lower()

elif environment == "windows":
    package_to_build = "windows-zip"

elif environment == "macos":
    package_to_build = "macos-app"

elif environment == "linux":
    package_to_build = "linux-appimage"


# Set optional values based on the package to be built
if package_to_build in ("windows-zip",):
    buildbase = "Win32GUI"
    name_icon = "icon.ico"

    include_files.append((os.path.join(path_assets, name_icon), os.path.join("lib", name_icon)))
    remove_files.append(("lib", "libcrypto-3.dll",)),
    remove_files.append(("lib", "libssl-3.dll",)),
    remove_files.append(("lib", "numpy", "core", "_simd.cp311-win_amd64.pyd")),
    move_files.append((("vcruntime140.dll",), ("lib", "vcruntime140.dll")))
    move_files.append((("vcruntime140_1.dll",), ("lib", "vcruntime140_1.dll")))

if package_to_build in ("macos-app",):
    remove_files.append(("lib", "torch", "bin", "protoc"))
    remove_files.append(("lib", "torch", "bin", "protoc-3.13.0.0"))
    remove_files.append(("lib", "torch", "lib", "libtorch.dylib"))
    remove_files.append(("lib", "torch", "lib", "libtorch_cpu.dylib"))
    remove_files.append(("lib", "torch", "lib", "libtorch_python.dylib"))
    remove_files.append(("lib", "numpy", ".dylibs", "libgfortran.5.dylib"))
    remove_files.append(("lib", "libcrypto.1.1.dylib"))
    remove_files.append(("lib", "libssl.1.1.dylib"))

if package_to_build in ("windows-zip", "linux-appimage"):
    remove_dirs.append(("lib", "ctypes", "macholib"))


# Determine the build configuration based on the package to be built
if package_to_build == "windows-zip":
    _platform = "win64"
    _distext = "zip"
    cx_action = "build_exe"

    def post_build_command():
        to_zip_file(buildpath, distpath)

elif package_to_build == "macos-app":
    _platform = "macos"
    _distext = "app"
    cx_action = "bdist_mac"

elif package_to_build == "linux-appimage":
    _platform = "linux"
    _distext = "appimage"
    cx_action = "bdist_appimage"

else:
    raise ValueError(f"Unsupported build environment: {environment}")

# Get the compression configuration for the current package
if not package_to_build in compression_lookup:
    print("Warning: No compression configuration found for the package to build, using no compression as default.")
compression: CompressionConfig | None = compression_lookup.get(package_to_build, None)

# Determine the correct path for the icon file
path_icon = os.path.join(path_assets, name_icon)

# Assemble the build path and final distribution filename
_dirname = f"handcode-{_platform}-v{buildversion}"
buildpath = os.path.join(path_dist, _dirname)
distpath = os.path.join(path_dist, f"{_dirname}{os.path.extsep}{_distext}")

# Add the build path to be cleaned up
if package_to_build in ("windows-zip", "macos-app", "linux-appimage"):
    clean_dirs.append(buildpath)
