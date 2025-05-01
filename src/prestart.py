import sys

def unpack_relevant_files():
    if not getattr(sys, "frozen", False):
        # if this is not a built package, skip prestart (i.e. dont unpack compressed files)
        return
    
    if "--test-start-behaviour" in sys.argv:
        # make sure that all libraries for prestart are loaded and thus not optimized away
        # but dont actually do something here (return), because this function is only meant when actually starting the program
        import os
        import threading
        import tkinter
        import lzma
        return
    
    import os

    path_lib = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "lib")
    path_unpacked = os.path.join(path_lib, "handcodeunpacked")

    if os.path.exists(path_unpacked):
        # if all files have already been unpacked, skip this step to reduce startup time
        return

    import tkinter

    style = {
        "bg_window": "#303030",
        "fg_text": "#D0D0D0",
    }

    root = tkinter.Tk()
    root.title("Unpacking files")
    root.geometry("300x50")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", lambda *_: 0)
    root.configure(bg=style["bg_window"])
    if os.name == "nt":
        root.iconbitmap(os.path.join(path_lib, "icon.ico"))
        
    tkinter.Label(root, text="HandCode is unpacking its files right now.\nThis may take a few minutes, but it only\nneeds to be done once after installation.", fg=style["fg_text"]).place(x=0, y=0, width=300, height=50)
    root.update()

    import lzma
    import threading

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

    def decompress_thread():
        decompresslargefiles(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "lib"), 3)
        open(path_unpacked, "w").close()
        root.after(0, root.destroy)

    threading.Thread(target=decompress_thread).start()
    root.mainloop()
