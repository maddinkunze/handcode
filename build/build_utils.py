import os
import sys
import time
import shutil
import zipfile
from build_common import path_setup

def to_zip_file(in_dir: str, out_file: str) -> None:
    print("Creating zip file... ", end="", flush=True)
    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for dirname, subdirs, files in os.walk(in_dir):
            for filename in files:
                zf.write(os.path.join(dirname, filename),
                         os.path.relpath(os.path.join(dirname, filename), os.path.join(in_dir, "..")))
    print("Done")

def check_existing_build(distpath: str) -> None:
    if not os.path.exists(distpath):
        return
    
    print("/-----------------------------------------------------------------\\")
    print("| WARNING! There already exists a build with this version number! |")
    print("| Press Ctrl-C to cancel the build. Auto-continue in 5 seconds... |")
    print("|            -  --  ---  ----  -----  ----  ---  --  -            |")
    #      |                    5...  4...  3...  2...  1...                 |
    print("|                  ", end="")
    for i in range(5, 0, -1): 
        print(f"  {i}", end="", flush=True)
        time.sleep(0.25)
        for i in range(3):
            print(".", end="", flush=True)
            time.sleep(0.25)
    print(                                                 "                 |")
    print("\\-----------------------------------------------------------------/")
    print()

def build_with_cxfreeze(mode: str) -> None:
    print(f"Building HandCode with cx_Freeze and python {sys.version}...")
    os.system(f"python \"{path_setup}\" {mode}")

def remove_build_files(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)
