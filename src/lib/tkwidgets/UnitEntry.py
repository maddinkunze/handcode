import tkinter as tk
import tkinter.font as tkf

class UnitEntry:
    def __init__(self, root, **kwargs):
        self.entry = tk.Entry(root, justify="right", relief=tk.FLAT, validate="focusout", validatecommand=self._onchange)
        self.unit = tk.Label(root)
        self.unittext = ""
        self.unitwidth = 0
        self.font = tkf.nametofont("TkDefaultFont")
        self.configure(**kwargs)
        self.listeners = dict()

    def configure(self, **kwargs):
        centry = {}
        cunit = {}

        if "bgentry" in kwargs:
            centry["bg"] = kwargs["bgentry"]
            cunit["bg"] = kwargs["bgentry"]

        if "fgentry" in kwargs:
            centry["fg"] = kwargs["fgentry"]
            
        if "fgunit" in kwargs:
            cunit["fg"] = kwargs["fgunit"]

        if "bgcursor" in kwargs:
            centry["insertbackground"] = kwargs["bgcursor"]

        if "font" in kwargs:
            self.font = kwargs["font"]
            centry["font"] = self.font
            cunit["font"] = self.font
            self.unitwidth = self.font.measure(self.unittext) + 5

        if "unit" in kwargs:
            self.unittext = kwargs["unit"]
            cunit["text"] = self.unittext
            self.unitwidth = self.font.measure(self.unittext) + 5

        if "bd" in kwargs:
            centry["bd"] = kwargs["bd"]

        if "highlightthickness" in kwargs:
            centry["highlightthickness"] = kwargs["highlightthickness"]

        if "relief" in kwargs:
            centry["relief"] = kwargs["relief"]

        if centry:
            self.entry.configure(**centry)
        if cunit:
            self.unit.configure(**cunit)

    def set(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)

    def get(self):
        return self.entry.get()

    def place(self, x, y, width):
        self.entry.place(x=x, y=y, width=width-self.unitwidth, height=20)
        self.unit.place(x=x+width-self.unitwidth, y=y, width=self.unitwidth, height=20)

    def _onchange(self):
        _name = "change"
        if not _name in self.listeners:
            return
        
        for listener in self.listeners[_name].values():
            listener()

        return True

    def addListener(self, name, listener, tag=None):
        if name not in self.listeners:
            self.listeners[name] = dict()

        if tag is None:
            tag = 0
            while f"{tag}" in self.listeners[name]:
                tag += 1

        self.listeners[name][tag] = listener

        return tag

    def removeListener(self, name, tag):
        if name not in self.listeners:
            return

        self.listeners[name].pop(tag, None)

    def callListeners(self, name, tag=None):
        if name not in self.listeners:
            return

        listeners = self.listeners[name]
        if tag is not None:
            if tag not in listeners:
                return
            listeners[tag]()

        for listener in listeners.values():
            listener()
