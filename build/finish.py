import os
import shutil
import pkgutil

path_build = os.path.join("build", "exe.win-amd64-3.6")
path_lib = os.path.join(path_build, "lib")

print("Copying neccessary files... ", end="")

path_tf = os.path.join(path_lib, "tensorflow")
path_tf_from = os.path.dirname(pkgutil.get_loader("tensorflow").get_filename())
copyfiles_tf = [
  ("python", "util", "lazy_loader.py"), 
  ("python", "layers", "maxout.py"), 
  ("python", "profiler", "profile_context.py"),
  ("python", "eager", "custom_gradient.py"),
  ("python", "eager", "execution_callbacks.py"),
  ("python", "ops", "gen_batch_ops.py"),
  ("python", "ops", "distributions", "transformed_distribution.py"),
  ("contrib", "__init__.py"),
  ("contrib", "rnn", "__init__.py"),
  ("contrib", "layers", "__init__.py"),
  ("contrib", "framework", "__init__.py"),
  ("contrib", "meta_graph_transform", "meta_graph_transform.py")
]
for file in copyfiles_tf:
    shutil.copyfile(os.path.join(path_tf_from, *file), os.path.join(path_tf, *file))

path_pb = os.path.join(path_lib, "google", "protobuf")
path_pb_from = os.path.dirname(pkgutil.get_loader("google.protobuf").get_filename())
shutil.copyfile(os.path.join(path_pb_from, "wrappers_pb2.py"), os.path.join(path_pb, "wrappers_pb2.py"))

print("Done")

print("Copying neccessary folders... ", end="")

copydirs_tf = [
  ("core",),
  ("contrib", "tpu"),
  ("contrib", "util"),
  ("contrib", "data"),
  ("contrib", "lite"),
  ("contrib", "learn"),
  ("contrib", "eager"),
  ("contrib", "linalg"),
  ("contrib", "lookup"),
  ("contrib", "metrics"),
  ("contrib", "summary"),
  ("contrib", "training"),
  ("contrib", "compiler"),
  ("contrib", "factorization"),
  ("contrib", "distributions"),
  ("contrib", "session_bundle"),
  ("contrib", "input_pipeline"),
  ("contrib", "receptive_field"),
  ("contrib", "linear_optimizer"),
  ("contrib", "rnn", "ops"),
  ("contrib", "rnn", "python", "ops"),
  ("contrib", "layers", "ops"),
  ("contrib", "layers", "python"),
  ("contrib", "framework", "python"),
  ("contrib", "losses", "python", "losses"),
]

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

for dir_tf in copydirs_tf:
    copytree(os.path.join(path_tf_from, *dir_tf), os.path.join(path_tf, *dir_tf))

print("Done")

print("Removing unneccessary files... ", end="")


try: os.remove(os.path.join(path_lib, "sqlite3.dll"))
except: pass
try: os.remove(os.path.join(path_lib, "tensorboard", "webfiles.zip"))
except: pass
try: os.remove(os.path.join(path_lib, "tensorflow", "python", "pywrap_tensorflow_internal.lib"))
except: pass

print("Done")

print("Removing unneccessary folders... ", end="")

deldirs = [
  ("asyncio",),
  ("ctypes", "macholib"),
  ("distutils", "command"),
  ("distutils", "tests"),
  ("handwriting", "logs"),
  ("multiprocessing", "dummy"),
  ("numpy", "core", "include"),
  ("numpy", "core", "lib"),
  ("numpy", "distutils"),
  ("numpy", "doc"),
  ("numpy", "f2py"),
  ("numpy", "random", "lib"),
  ("pytz", "zoneinfo"),
  ("scipy", "_build_utils"),
  ("sklearn", "_build_utils"),
  ("tensorboard", "pip_package"),
  ("tcltk", "tcl8.6", "encoding"),
  ("tcltk", "tcl8.6", "http1.0"),
  ("tcltk", "tcl8.6", "msgs"),
  ("tcltk", "tcl8.6", "opt0.4"),
  ("tcltk", "tcl8.6", "tzdata"),
  ("tcltk", "tk8.6", "demos"),
  ("tcltk", "tk8.6", "images"),
  ("tcltk", "tk8.6", "msgs"),
  ("tkinter", "test"),
  ("tensorflow", "include"),
]

for item in deldirs:
    shutil.rmtree(os.path.join(path_lib, *item), ignore_errors=True)

path_mpl_data = os.path.join(path_lib, "matplotlib", "mpl-data")
for item in os.listdir(path_mpl_data):
    path_item = os.path.join(path_mpl_data, item)
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
