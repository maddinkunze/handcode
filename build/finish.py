import os
import sys
import time
import lzma
import shutil
import pkgutil
import traceback

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
#  ("_asyncio.pyd",),
#  ("_bz2.pyd",),
#  ("_decimal.pyd",),
#  ("_elementtree.pyd",),
#  ("_hashlib.pyd",),
#  ("_queue.pyd",),
#  ("_ssl.pyd",),
#  ("_testbuffer.pyd",),
#  ("_uuid.pyd",),
#  ("pyexpat.pyd",),
#  ("sqlite.dll",),
#  ("libcrypto-3.dll",),
#  ("libssl-3.dll",),
#  ("tensorflow", "python", "_pywrap_tensorflow_internal.lib"),
#  ("tensorflow", "python", "framework", "_errors_test_helper.pyd"),
#  ("tensorflow", "python", "framework", "_op_def_util.pyd"),
#  ("tensorflow", "python", "framework", "_python_memory_checker_helper.pyd"),
#  ("tensorflow", "python", "framework", "_pywrap_python_api_info.pyd"),
#  ("tensorflow", "python", "frameword", "_pywrap_python_api_parameter_converter.pyd"),
#  ("tensorflow", "python", "grappler", "_pywrap_tf_item.pyd"),
#  ("tensorflow", "python", "util", "_pywrap_kernel_registry.pyd"),
#  ("tensorflow", "python", "util", "_pywrap_stat_summarizer.pyd"),
#  ("tensorflow", "python", "util", "_pywrap_transform_graph.pyd"),
#  ("tensorflow", "lite", "python", "optimize", "_pywrap_tensorflow_lite_calibration_wrapper.pyd"),
#  ("tensorflow", "tsl", "python", "lib", "core", "bfloat16.so"),
#  ("numpy", "core", "_simd.cp311-win_amd64.pyd"),
#  ("certifi", "cacert.pem"),
]

for path in delfiles:
    try: os.remove(os.path.join(path_lib, *path))
    except: pass


def deletefilestemplate(path, filterf):
    for item in os.listdir(path):
        path_item = os.path.join(path, item)

        if os.path.isdir(path_item):
            deletefilestemplate(path_item, filterf)
            continue

        if os.path.isfile(path_item) and filterf(path, item):
            os.remove(path_item)

deletefilestemplate(os.path.join(path_lib, "numpy"), lambda _, f: f.endswith("pyi") or f.endswith("pxd"))

print("Done")

print("Removing unneccessary folders... ", end="")
sys.stdout.flush()

deldirs = [
#  ("ctypes", "macholib"),
#  ("distutils", "command"),
#  ("distutils", "tests"),
#  ("handwriting", "logs"),
#  ("numpy", "_pyinstaller"),
##  ("numpy", "_typing"),
#  ("numpy", "core", "include"),
#  ("numpy", "core", "lib"),
#  ("numpy", "array_api", "tests"),
#  ("numpy", "distutils"),
#  ("numpy", "doc"),
#  ("numpy", "f2py"),
#  ("numpy", "random", "lib"),
#  ("numpy", "testing", "tests"),
#  ("dateutil", "zoneinfo"),
#  ("pytz", "zoneinfo"),
#  ("tensorboard",),
#  ("google", "_upb"),
#  ("google", "auth"),
#  ("google", "oauth"),
#  ("importlib", "metadata"),
#  ("tcl8",),
#  ("tcl8.6", "encoding"),
#  ("tcl8.6", "http1.0"),
#  ("tcl8.6", "msgs"),
#  ("tcl8.6", "opt0.4"),
#  ("tcl8.6", "tzdata"),
#  ("tk8.6", "demos"),
#  ("tk8.6", "images"),
#  ("tk8.6", "msgs"),
#  ("tkinter", "test"),
#  ("tensorflow", "include"),
#  ("tensorflow", "xla_aot_runtime_src"),
#  ("pkg_ressources",),
#  ("html",),
#  ("google", "oauth2"),
#  ("PIL",),
#  ("pyparsing",),
#  ("requests", "packages"),
]

for item in deldirs:
    shutil.rmtree(os.path.join(path_lib, *item), ignore_errors=True)

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


print("Optimizing libraries... ")

# tensorflow_prob
try:
    # raise NotImplementedError()
    print("tensorflow_probability... ", end="")
    path_tf_prob = os.path.join(path_lib, "tensorflow_probability")

    import tensorflow_probability as tf_prob
    tf_prob_init = os.path.realpath(tf_prob.__file__)
    tf_prob_init_to = os.path.join(path_tf_prob, "__init__.py")

    try: os.remove(f"{tf_prob_init_to}c")
    except: pass

    file_from = open(tf_prob_init, "r")
    file_to = open(tf_prob_init_to, "w")
    _i = 0
    for line in file_from.read().split("\n"):
        if _i:
            file_to.write("\n")
        if "from tensorflow_probability import substrates" in line:
            continue

        file_to.write(line)
        _i = 1
    file_from.close()
    file_to.close()

    shutil.rmtree(os.path.join(path_tf_prob, "substrates"), ignore_errors=True)
    print("Done")
except NotImplementedError:
    pass
except:
    print(f"\ntensorflow_probability failed:\n{traceback.format_exc()}")

# remove unused files (open program and look which files were not accessed since opening the program)
def removefilesthathavenotbeenaccessed(path, since, excludes):
    for item in os.listdir(path):
        path_item = os.path.join(path, item)

        exclude = False
        for ep in excludes:
            if path_item.endswith(os.path.join(*ep)):
                exclude = True
                break
        if exclude:
            continue

        if os.path.isdir(path_item):
            removefilesthathavenotbeenaccessed(path_item, since, excludes)
        if os.path.isfile(path_item):
            if os.path.getatime(path_item) > since:
                continue
            
            try: os.remove(path_item)
            except: pass

try:
    # raise NotImplementedError()
    start = time.time() - 5
    print("automatic removal... ")
    time.sleep(5)
    path_exe = os.path.join(path_build, "HandCode.exe")
    os.system(f"{path_exe} --test-start-behaviour")

    excludes_autoremove = [
        ("handwriting", "styles"),
        #("handwriting", "checkpoints")
    ]
    removefilesthathavenotbeenaccessed(path_lib, start, excludes_autoremove)
except KeyboardInterrupt:
    pass
except:
    print(f"automatic removal failed:\n{traceback.format_exc()}")
print("Done")


print("Compressing large files (this may take a few minutes)... ")

filters_compression = [
    {"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME},
]

def compresslargefiles(basedir, minsize, compressfactor, excludes, maxlevel):
    if maxlevel < 0:
        return
    
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
  "tkinter",
  "tcl86t.dll",
  "tk86t.dll",
  "library.zip"
]
compresslargefiles(path_lib, 500_000, 0.6, excludes_compress, 3)

print("Done")
