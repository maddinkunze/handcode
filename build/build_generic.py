import os
import sys
from build_common import distpath, path_setup

def check_existing_build() -> None:
    if not os.path.exists(distpath):
        return
    
    print("/-----------------------------------------------------------------\\")
    print("| WARNING! There already exists a build with this version number! |")
    print("\\-----------------------------------------------------------------/")
    print()

def build_with_cxfreeze(mode="build_exe") -> None:
    check_existing_build()
    print(f"Building HandCode with cx_Freeze and python {sys.version}...")
    os.system(f"python \"{path_setup}\" {mode}")

def build_generic():
    build_with_cxfreeze()

if __name__ == "__main__":
    build_generic()