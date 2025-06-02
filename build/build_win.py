import os
import zipfile
from build_generic import build_with_cxfreeze
from build_common import buildpath, distpath

def build_win() -> None:
    build_with_cxfreeze()
    to_zip_file()

def to_zip_file() -> None:
    print("Creating zip file... ", end="")
    with zipfile.ZipFile(distpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for dirname, subdirs, files in os.walk(buildpath):
            for filename in files:
                zf.write(os.path.join(dirname, filename),
                         os.path.relpath(os.path.join(dirname, filename), os.path.join(buildpath, "..")))
    print("Done")

if __name__ == "__main__":
    build_win()
