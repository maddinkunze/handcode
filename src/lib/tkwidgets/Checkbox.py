import tkinter as tk

class Checkbox:
    def __init__(self, root, **kwargs):
        self.var = tk.BooleanVar()
        self.chk = tk.Checkbutton(root, variable=self.var, relief=tk.FLAT, borderwidth=0, command=self._onchange)
        self.configure(**kwargs)
        self.listeners = dict()

    def configure(self, **kwargs):
        ccheck = dict()

        if "label" in kwargs:
            ccheck["text"] = kwargs["label"]

        if "bglabel" in kwargs:
            ccheck["bg"] = kwargs["bglabel"]
            ccheck["activebackground"] = kwargs["bglabel"]

        if "bgcheck" in kwargs:
            ccheck["selectcolor"] = kwargs["bgcheck"]

        if "fg" in kwargs:
            ccheck["fg"] = kwargs["fg"]
            ccheck["activeforeground"] = kwargs["fg"]

        if "font" in kwargs:
            ccheck["font"] = kwargs["font"]

        if "state" in kwargs:
            ccheck["state"] = kwargs["state"]

        if "bd" in kwargs:
            ccheck["bd"] = kwargs["bd"]

        if "highlightthickness" in kwargs:
            ccheck["highlightthickness"] = kwargs["highlightthickness"]

        if "relief" in kwargs:
            ccheck["relief"] = kwargs["relief"]

        if ccheck:
            self.chk.configure(**ccheck)
        
    def get(self):
        return self.var.get()

    def set(self, value):
        return self.var.set(value)

    def place(self, x, y, height):
        self.chk.place(x=x, y=y, height=height)

    def _onchange(self):
        _name = "change"
        if not _name in self.listeners:
            return
        
        for listener in self.listeners[_name].values():
            listener()

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
