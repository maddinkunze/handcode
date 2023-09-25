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
            font = kwargs["font"]
            clabel["font"] = font
            centry["font"] = font

        if "label" in kwargs:
            clabel["text"] = kwargs["label"]

        if "unit" in kwargs:
            centry["unit"] = kwargs["unit"]

        if clabel:
            self.label.configure(**clabel)
        if centry:
            self.entry.configure(**centry)

    def set(self, text):
        self.entry.set(text)

    def get(self):
        return self.entry.get()

    def place(self, x, y, width):
        self.label.place(x=x, y=y, width=width, height=20)
        self.entry.place(x=x, y=y+20, width=width)
