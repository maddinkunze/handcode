import os
import bz2
import shutil
from cx_Freeze import build_exe
from build_common import _remove_file_filter
from build_config import CompressionConfig, compression, move_files, remove_files, remove_dirs, remove_files_pattern


def move_build_files(build_path: str):
    for path, target in move_files:
        path_from = os.path.join(build_path, *path)
        path_to = os.path.join(build_path, *target)
        print(f"Moving {path_from} to {path_to}")
        os.rename(path_from, path_to)

def remove_files_template(build_path: str):
    for path, template in remove_files_pattern:
        _remove_files_template(os.path.join(build_path, *path), template)

def _remove_files_template(path: str, filterf: _remove_file_filter):
    for item in os.listdir(path):
        path_item = os.path.join(path, item)

        if os.path.isdir(path_item):
            _remove_files_template(path_item, filterf)
            continue

        if os.path.isfile(path_item) and filterf(path, item):
            os.remove(path_item)

def remove_unnecessary_files(build_path: str):
    for path in remove_files:
        path_full = os.path.join(build_path, *path)
        if not os.path.isfile(path_full):
            continue

        print(f"Removing {path_full}")
        os.remove(path_full)

def remove_unnecessary_dirs(build_path: str):
    for path in remove_dirs:
        path_full = os.path.join(build_path, *path)
        if not os.path.isdir(path_full):
            continue

        print(f"Removing directory {path_full}")
        shutil.rmtree(path_full, ignore_errors=True)

def compress_large_files(build_path: str, config: CompressionConfig):
    for path in config.files:
        path_full = os.path.join(build_path, *path)
        if os.path.isdir(path_full):
            print(f"Compressing files in {path_full}")
            _compress_large_files(path_full, 500_000, 0.6, config.ext, [], config.depth)
        elif os.path.isfile(path_full):
            _compress_large_file(path_full, 500_000, 0.6, config.ext)

def _compress_large_files(basedir: str, minsize: int, compressfactor: float, ext: str, excludes: list[str], maxlevel: int):
    if maxlevel < 0:
        return
    
    for item in os.listdir(basedir):
        path_item = os.path.join(basedir, item)
        if (item in excludes) or (path_item in excludes):
            continue
        
        if os.path.isdir(path_item):
            _compress_large_files(path_item, minsize, compressfactor, ext, excludes, maxlevel-1)
        elif os.path.isfile(path_item):
            _compress_large_file(path_item, minsize, compressfactor, ext)

def _compress_large_file(path: str, minsize: int, compressfactor: float, ext: str):
    filesize_orig = os.stat(path).st_size
    if filesize_orig < minsize:
        return
    path_compressed = path + compression.ext

    print(f"Compressing {path}({compression.ext})", end="", flush=True)
    file_orig = open(path, "rb")
    file_compressed = bz2.open(path_compressed, "wb")
    file_compressed.write(file_orig.read())
    file_compressed.close()
    file_orig.close()
    
    filesize_compressed = os.stat(path_compressed).st_size
    path_del = path
    if (filesize_compressed / filesize_orig) > compressfactor:
        print(f" (discarded)", end="")
        path_del = path_compressed
    os.remove(path_del)
    print()

def optimize_build(build_path: str):
    """
    Optimize the build by removing unnecessary files and directories.
    This is useful for reducing the size of the final distribution.
    """
    move_build_files(build_path)
    remove_unnecessary_dirs(build_path)
    remove_unnecessary_files(build_path)
    remove_files_template(build_path)
    if compression:
        compress_large_files(build_path, compression)

# patch build_exe.run to allow us to remove files between build_exe and bdist_*
def patch_build_exe_run():
    """
    Patch the build_exe.run method to allow us to remove files and directories after the build is done.
    This is useful for removing unnecessary files that are not needed in the final distribution.
    """
    _old_build_exe_run = build_exe.run
    def _new_build_exe_run(self: build_exe):
        _old_build_exe_run(self)
        optimize_build(self.build_exe)        
    build_exe.run = _new_build_exe_run
