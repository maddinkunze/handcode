import os
import sys
import typing

_package_key = "HANDCODE_PACKAGE"
_remove_file_filter = typing.Callable[[str, str], bool]

path_build = os.path.dirname(os.path.abspath(__file__))
path_dist = os.path.join(path_build, "..", "dist")
path_setup = os.path.join(path_build, "build_setup.py")

path_src = os.path.join(path_build, "..", "src")
path_lib = os.path.join(path_src, "lib")
path_assets = os.path.join(path_src, "assets")

sys.path.append(path_src)
from common import CompressionConfig
from common import version_handcode as buildversion, path_icon, compression_lookup, environment
sys.path.pop()

buildname = "HandCode"
buildcpr = "© Martin Kunze - https://github.com/maddinkunze/handcode"
