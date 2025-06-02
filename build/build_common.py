import os
import sys
import platform

path_build = os.path.dirname(os.path.abspath(__file__))
path_dist = os.path.join(path_build, "dist")
path_setup = os.path.join(path_build, "build_setup.py")

path_src = os.path.join(path_build, "..", "src")
path_lib = os.path.join(path_src, "lib")
if sys.platform == "win32":
    path_icon = os.path.join(path_lib, "icon.ico")
else:
    path_icon = os.path.join(path_lib, "icon.png")

_platform = None
if sys.platform == "win32":
    _platform = "win64"
    _distext = "zip"
elif sys.platform == "darwin":
    _platform = "macos"
    _distext = "app"
assert _platform is not None, "Unknown platform to build for: " + sys.platform

sys.path.append(path_src)
from common import version_handcode as buildversion, use_compression, ext_compression, files_compressed, compression_depth
sys.path.pop()
sys.path.pop()

_dirname = f"handcode-{_platform}-{buildversion}"

buildname = "HandCode"
buildcpr = "© Martin Kunze - https://github.com/maddinkunze/handcode"
buildpath = os.path.join(path_dist, _dirname)
distpath = os.path.join(path_dist, f"{_dirname}{os.path.extsep}{_distext}")