import tkinter as tk
from . import UnitEntry

class LabeledEntry:
    def __init__(self, root, **kwargs):
        self.label = tk.Label(root)
        self.entry = UnitEntry(root)
        self.configure(**kwargs)

        self.addListener = self.entry.addListener
        self.removeListener = self.entry.removeListener
        self.callListeners = self.entry.callListeners

    def configure(self, **kwargs):
        clabel = {}
        centry = {}

        if "bglabel" in kwargs:
            clabel["bg"] = kwargs["bglabel"]

        if "fglabel" in kwargs:
            clabel["fg"] = kwargs["fglabel"]

        if "bgentry" in kwargs:
            centry["bgentry"] = kwargs["bgentry"]
            
        if "fgentry" in kwargs:
            centry["fgentry"] = kwargs["fgentry"]
            
        if "fgunit" in kwargs:
            centry["fgunit"] = kwargs["fgunit"]

        if "bgcursor" in kwargs:
            centry["bgcursor"] = kwargs["bgcursor"]

        if "font" in kwargs:
            centry["font"] = kwargs["font"]

        if "fontlabel" in kwargs:
            clabel["font"] = kwargs["fontlabel"]

        if "label" in kwargs:
            clabel["text"] = kwargs["label"]

        if "unit" in kwargs:
            centry["unit"] = kwargs["unit"]

        if "bd" in kwargs:
            centry["bd"] = kwargs["bd"]

        if "highlightthickness" in kwargs:
            centry["highlightthickness"] = kwargs["highlightthickness"]

        if "relief" in kwargs:
            centry["relief"] = kwargs["relief"]

        if clabel:
            self.label.configure(**clabel)
        if centry:
            self.entry.configure(**centry)

    def set(self, text):
        self.entry.set(text)

    def get(self):
        return self.entry.get()

    def place(self, x, y, width, relx=0, rely=0, anchor=tk.NW):
        self.label.place(x=x, y=y, width=width, height=20, relx=relx, rely=rely, anchor=anchor)
        self.entry.place(x=x, y=y+20, width=width, relx=relx, rely=rely, anchor=anchor)
