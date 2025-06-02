import sys

def unpack_relevant_files():
    if not getattr(sys, "frozen", False):
        # if this is not a built package, skip prestart (i.e. dont unpack compressed files)
        return

    from common import use_compression, path_exe_dir, path_lib, ext_compression, files_compressed, compression_depth, set_tk_icon

    if not use_compression:
        return

    import os

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
    root.geometry("300x65")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", lambda *_: 0)
    root.configure(bg=style["bg_window"])
    set_tk_icon(root)
        
    tkinter.Label(root, text="HandCode is unpacking its files right now.\nThis may take a few minutes, but it only\nneeds to be done once after installation.", fg=style["fg_text"]).place(x=0, y=0, width=300, height=62)
    root.update()

    import lzma
    import threading

    def decompress_large_files(path, maxlevel):
        if maxlevel < 0:
            return
    
        for item in os.listdir(path):
            path_item = os.path.join(path, item)
        
            if os.path.isdir(path_item):
                decompress_large_files(path_item, maxlevel-1)
            elif os.path.isfile(path_item):
                decompress_large_file(path_item)

    def decompress_large_file(path: str):
        if not path.endswith(ext_compression):
            return
        path_decompressed = path[:-len(ext_compression)]

        file_orig = lzma.open(path, "rb")
        file_compressed = open(path_decompressed, "wb")
        file_compressed.write(file_orig.read())
        file_compressed.close()
        file_orig.close()

        os.remove(path)

    def decompress_thread():
        for path in files_compressed:
            path_actual = os.path.join(path_exe_dir, *path)
            if os.path.isdir(path_actual):
                decompress_large_files(path_actual, compression_depth)
                continue

            path_actual += ext_compression
            if os.path.isfile(path_actual):
                decompress_large_file(path_actual)
                continue

        # create an empty file to indicate that unpacking is done, so we can skip this step in the future
        open(path_unpacked, "w").close()
        root.after(0, root.destroy)

    threading.Thread(target=decompress_thread).start()
    root.mainloop()
