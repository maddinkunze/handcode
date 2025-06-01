import os
import re
import sys

path_exe_dir = os.path.dirname(os.path.realpath(sys.executable if getattr(sys, "frozen", False) else __file__))
path_data = os.path.join(path_exe_dir, "data")
path_settings = os.path.join(path_data, "settings.json")
path_lib = os.path.join(path_exe_dir, "lib")

version_handcode = None # specify handcode version here, if it cannot be determined automatically
if getattr(sys, "frozen", False):
    # frozen builds will not contain the pyproject.toml file, but we will pass the version to cx_freeze as a build constant
    from BUILD_CONSTANTS import handcode_version # type: ignore[import-not-found]
elif version_handcode is None:
    # for non-frozen builds, we can read the version from pyproject.toml
    re_version = re.compile(r"^version\s*=\s*['\"]([^'\"]+)['\"]\s*$", re.MULTILINE)
    path_pyproject = os.path.join(path_exe_dir, os.pardir, "pyproject.toml")
    assert os.path.exists(path_pyproject), "Could not determine program version because pyproject.toml was not found, please specify the version manually in common.py"
    with open(path_pyproject, "r", encoding="utf-8") as file_pyproject:
        match_version = re.search(re_version, file_pyproject.read())
    assert match_version is not None, "Could not determine program version from pyproject.toml, please specify it manually in common.py"
    version_handcode = match_version.group(1)
assert version_handcode is not None, "Could not determine program version, please specify it manually in common.py"

sys.path.append(path_lib) # for clean build reasons we dont include lib.handwriting
