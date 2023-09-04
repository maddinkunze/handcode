import os
import sys
import lzma
import shutil
import pkgutil

path_build = os.path.join("dist", "handcode-win64")
path_lib = os.path.join(path_build, "lib")

print("Moving files... ", end="")

movefiles_tolib = ["vcruntime140.dll", "vcruntime140_1.dll", "frozen_application_license.txt"]
for file in movefiles_tolib:
    try: os.rename(os.path.join(path_build, file), os.path.join(path_lib, file))
    except: pass

print("Done")

print("Copying neccessary folders... ", end="")
sys.stdout.flush()

def copytree(src, dst):
    if not os.path.isdir(dst):
        os.mkdir(dst)
        
    for item in os.listdir(src):
        path_item_src = os.path.join(src, item)
        path_item_dst = os.path.join(dst, item)
        if os.path.isdir(path_item_src):
            if item == "__pycache__": continue
            copytree(path_item_src, path_item_dst)
        elif os.path.isfile(path_item_src):
            if os.path.isfile(path_item_dst + "c"):
                continue
            if os.path.isfile(path_item_dst + "d"):
                continue
            shutil.copyfile(path_item_src, path_item_dst)

print("Done")

print("Removing unneccessary files... ", end="")
sys.stdout.flush()

delfiles = [
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
  ("sqlite.dll",),
  ("libcrypto-3.dll",),
  ("libssl-3.dll",),
  ("tensorflow", "python", "_pywrap_tensorflow_internal.lib"),
]

for path in delfiles:
    try: os.remove(os.path.join(path_lib, *path))
    except: pass

print("Done")

print("Removing unneccessary folders... ", end="")
sys.stdout.flush()

deldirs = [
  ("ctypes", "macholib"),
  ("distutils", "command"),
  ("distutils", "tests"),
  ("handwriting", "logs"),
  ("numpy", "_pyinstaller"),
  ("numpy", "_typing"),
  ("numpy", "core", "include"),
  ("numpy", "core", "lib"),
  ("numpy", "array_api", "tests"),
  ("numpy", "distutils"),
  ("numpy", "doc"),
  ("numpy", "f2py"),
  ("numpy", "random", "lib"),
  ("numpy", "testing", "tests"),
  ("dateutil", "zoneinfo"),
  ("pytz", "zoneinfo"),
  ("scipy", "_build_utils"),
  ("tensorboard",),
  ("google", "_upb"),
  ("google", "auth"),
  ("google", "oauth"),
  ("importlib", "metadata"),
  ("matplotlib","backends"),
  ("matplotlib","sphinxext"),
  ("tcl8",),
  ("tcl8.6", "encoding"),
  ("tcl8.6", "http1.0"),
  ("tcl8.6", "msgs"),
  ("tcl8.6", "opt0.4"),
  ("tcl8.6", "tzdata"),
  ("tk8.6", "demos"),
  ("tk8.6", "images"),
  ("tk8.6", "msgs"),
  ("tkinter", "test"),
  ("tensorflow", "include"),
  ("pkg_ressources", "_vendor"),
  ("requests", "packages"),
]

for item in deldirs:
    shutil.rmtree(os.path.join(path_lib, *item), ignore_errors=True)

path_mpl_data = os.path.join(path_lib, "matplotlib", "mpl-data")
for item in os.listdir(path_mpl_data):
    path_item = os.path.join(path_mpl_data, item)
    if not os.path.isdir(path_item):
        continue
    shutil.rmtree(path_item, ignore_errors=True)

path_scipy = os.path.join(path_lib, "scipy")
for item in os.listdir(path_scipy):
    path_item = os.path.join(path_scipy, item, "tests")
    if not os.path.isdir(path_item):
        continue
    shutil.rmtree(path_item, ignore_errors=True)

def removeunneccessaryfolders(basedir):
    if not os.path.isdir(basedir):
        return 1

    count = 0
    for item in os.listdir(basedir):
        if item in ["tensorflow"]:
            continue
        path_item = os.path.join(basedir, item)
        # remove folders that are meant to be temporary (like __pycaches__ and ~olders)
        if (item == "__pycache__") or (os.path.isdir(path_item) and item.startswith("~")):
            shutil.rmtree(path_item)
            continue
        _count = removeunneccessaryfolders(path_item)
        # remove empty folders
        #if not _count:
        #    shutil.rmtree(path_item, ignore_errors=True)
        count += _count
    return count

removeunneccessaryfolders(path_lib)

print("Done")


print("Compressing large files (this may take a few minutes)... ", end="")
sys.stdout.flush()

def compresslargefiles(basedir, minsize, compressfactor, excludes, maxlevel):
    if maxlevel < 0:
        return

    filters_compression = [
        {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME},
    ]
    
    for item in os.listdir(basedir):
        if maxlevel == 3: print(item)
        path_item = os.path.join(basedir, item)
        if (item in excludes) or (path_item in excludes):
            continue
        
        if os.path.isdir(path_item):
            compresslargefiles(path_item, minsize, compressfactor, excludes, maxlevel-1)
        elif os.path.isfile(path_item):
            filesize_orig = os.stat(path_item).st_size
            if filesize_orig < minsize:
                continue
            path_compressed = path_item + ".lzma"

            file_orig = open(path_item, "rb")
            file_compressed = lzma.open(path_compressed, "wb", filters=filters_compression)
            file_compressed.write(file_orig.read())
            file_compressed.close()
            file_orig.close()
            
            filesize_compressed = os.stat(path_compressed).st_size
            path_del = path_compressed
            if (filesize_compressed / filesize_orig) < compressfactor:
                path_del = path_item
            os.remove(path_del)

excludes_compress = [
  "lzma",
  "library.zip"
]
compresslargefiles(path_lib, 500_000, 0.6, excludes_compress, 3)

print("Done")
