import os
import sys

version_handcode = "0.4.2"
path_exe = os.path.dirname(os.path.realpath(sys.executable if getattr(sys, "frozen", False) else __file__))
path_data = os.path.join(path_exe, "data")
path_settings = os.path.join(path_data, "settings.json")
path_lib = os.path.join(path_exe, "lib")
sys.path.append(path_lib) # for clean build reasons we dont include lib.handwriting