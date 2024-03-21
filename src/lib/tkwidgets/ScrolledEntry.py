import tkinter as tk
import tkinter.ttk as ttk

class ScrolledEntry:
    def __init__(self, root, **kwargs):
        self.entry = tk.Text(root, wrap=tk.NONE, relief=tk.FLAT)
        self.scrollX = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.entry.xview)
        self.scrollY = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.entry.yview)
        self.entry.configure(xscrollcommand=self.scrollX.set, yscrollcommand=self.scrollY.set)
        self.configure(**kwargs)

    def get(self):
        return self.entry.get(0.0, tk.END)[:-1]

    def set(self, text):
        self.entry.delete(0.0, tk.END)
        self.entry.insert(0.0, text)

    def append(self, text):
        self.entry.insert(tk.END, text)

    def configure(self, **kwargs):
        centry = {}
        cscrollX = {}
        cscrollY = {}

        if "bgentry" in kwargs:
            centry["bg"] = kwargs["bgentry"]

        if "fgentry" in kwargs:
            centry["fg"] = kwargs["fgentry"]
        
        if "bgcursor" in kwargs:
            centry["insertbackground"] = kwargs["bgcursor"]

        if "font" in kwargs:
            centry["font"] = kwargs["font"]

        if "stylescrollx" in kwargs:
            cscrollX["style"] = kwargs["stylescrollx"]

        if "stylescrolly" in kwargs:
            cscrollY["style"] = kwargs["stylescrolly"]

        if "bd" in kwargs:
            centry["bd"] = kwargs["bd"]

        if "highlightthickness" in kwargs:
            centry["highlightthickness"] = kwargs["highlightthickness"]

        if "relief" in kwargs:
            centry["relief"] = kwargs["relief"]

        if centry:
            self.entry.configure(centry)
        if cscrollX:
            self.scrollX.configure(cscrollX)
        if cscrollY:
            self.scrollY.configure(cscrollY)

    def place(self, x, y, width, height):
        self.entry.place(x=x, y=y, width=width-15, height=height-15)
        self.scrollX.place(x=x, y=y+height-15, width=width-15, height=15)
        self.scrollY.place(x=x+width-15, y=y, width=15, height=height-15)
