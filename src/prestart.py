import os
import sys
import lzma

def decompresslargefiles(basedir, maxlevel):
    if maxlevel < 0:
        return
    
    for item in os.listdir(basedir):
        path_item = os.path.join(basedir, item)
        
        if os.path.isdir(path_item):
            decompresslargefiles(path_item, maxlevel-1)
        elif os.path.isfile(path_item):
            _ext = ".lzma"
            if not item.endswith(_ext):
                continue
            path_decompressed = path_item[:-len(_ext)]

            file_orig = lzma.open(path_item, "rb")
            file_compressed = open(path_decompressed, "wb")
            file_compressed.write(file_orig.read())
            file_compressed.close()
            file_orig.close()
            
            os.remove(path_item)

def prestart():
    if not sys.frozen:
        return
    decompresslargefiles("lib", 3)
