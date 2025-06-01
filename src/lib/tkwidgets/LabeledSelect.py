import tkinter as tk

class LabeledSelect:
    def __init__(self, root, **kwargs):
        self.listeners = {}
        self._options = {}
        self.label = tk.Label(root)
        self.var = tk.StringVar()
        self.select = tk.OptionMenu(root, self.var, "")
        self.select.configure(highlightthickness=0, relief=tk.FLAT, borderwidth=0)
        self.select["menu"].configure(relief=tk.FLAT)
        self.configure(**kwargs)

    def configure(self, **kwargs):
        clabel = {}
        cselect = {}
        cmenu = {}

        if "bglabel" in kwargs:
            clabel["bg"] = kwargs["bglabel"]

        if "fglabel" in kwargs:
            clabel["fg"] = kwargs["fglabel"]

        if "bgselect" in kwargs:
            cselect["bg"]  = kwargs["bgselect"]
            cmenu["bg"] = kwargs["bgselect"]

        if "bgselect:hover" in kwargs:
            cselect["activebackground"] = kwargs["bgselect:hover"]
            cmenu["activebackground"] = kwargs["bgselect:hover"]

        if "fgselect" in kwargs:
            cselect["fg"] = kwargs["fgselect"]
            cmenu["fg"] = kwargs["fgselect"]

        if "fgselect:hover" in kwargs:
            cselect["activeforeground"] = kwargs["fgselect:hover"]
            cmenu["activeforeground"] = kwargs["fgselect:hover"]

        if "font" in kwargs:
            font = kwargs["font"]
            cselect["font"] = font
            cmenu["font"] = font

        if "fontlabel" in kwargs:
            clabel["font"] = kwargs["fontlabel"]
            
        if "label" in kwargs:
            clabel["text"] = kwargs["label"]

        if "state" in kwargs:
            cselect["state"] = kwargs["state"]

        if "options" in kwargs:
            self.setOptions(kwargs["options"])

        if clabel:
            self.label.configure(**clabel)
        if cselect:
            self.select.configure(**cselect)
        if cmenu:
            self.select["menu"].configure(**cmenu)

    def setOptions(self, options):
        if self.get() not in options:
            self.set("")

        self.select["menu"].delete(0, tk.END)
        self._options = {}
        if isinstance(options, dict):
            self._options = options
        for option in options:
            name = self._options.get(option, option)
            self.select["menu"].add_command(label=name, command=lambda _opt=option: self.set(_opt))

    def get(self):
        value = self.var.get()
        for opt, name in self._options.items():
            if name == value:
                return opt
        return value

    def set(self, value, *, noevent=False):
        _prev = self.var.get()
        value = self._options.get(value, value)
        if _prev == value:
            return
        if not noevent:
            self._onbeforechange()
        self.var.set(value)
        if not noevent:
            self._onchange()

    def place(self, x, y, width):
        self.label.place(x=x, y=y, width=width, height=20)
        self.select.place(x=x, y=y+20, width=width, height=20)

    def _onbeforechange(self):
       self._callListeners("beforechange")

    def _onchange(self):
        self._callListeners("change")

    def _callListeners(self, name):
        if name not in self.listeners:
            return

        listeners = self.listeners[name]
        for listener in listeners.values():
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