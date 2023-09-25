import tkinter as tk

class LabeledScale:
    def __init__(self, root, **kwargs):
        self.label = tk.Label(root)
        self.scale = tk.Scale(root, orient=tk.HORIZONTAL, showvalue=0, tickinterval=0, relief=tk.FLAT, borderwidth=0)
        self.tooltip = tk.Label(root)
        self.configure(**kwargs)

    def configure(self, **kwargs):
        clabel = {}
        cscale = {}
        ctooltip = {}

        if "bglabel" in kwargs:
            clabel["bg"] = kwargs["bglabel"]
            cscale["highlightbackground"] = kwargs["bglabel"]
            ctooltip["bg"] = kwargs["bglabel"]

        if "fglabel" in kwargs:
            clabel["fg"] = kwargs["fglabel"]

        if "fgtooltip" in kwargs:
            ctooltip["fg"] = kwargs["fgtooltip"]

        if "bgscale" in kwargs:
            cscale["troughcolor"] = kwargs["bgscale"]

        if "fgscale" in kwargs:
            cscale["bg"] = kwargs["fgscale"]

        if "fgscale:hover" in kwargs:
            cscale["activebackground"] = kwargs["fgscale:hover"]

        if "state" in kwargs:
            cscale["state"] = kwargs["state"]

        if "font" in kwargs:
            clabel["font"] = kwargs["font"]

        if "fonttooltip" in kwargs:
            ctooltip["font"] = kwargs["fonttooltip"]

        if "label" in kwargs:
            clabel["text"] = kwargs["label"]

        if "description" in kwargs:
            ctooltip["text"] = kwargs["description"]

        if "start" in kwargs:
            cscale["from_"] = kwargs["start"]

        if "end" in kwargs:
            cscale["to"] = kwargs["end"]

        if "step" in kwargs:
            cscale["resolution"] = kwargs["step"]

        if clabel:
            self.label.configure(clabel)
        if cscale:
            self.scale.configure(cscale)
        if ctooltip:
            self.tooltip.configure(ctooltip)

    def set(self, value):
        self.scale.set(value)

    def get(self):
        return self.scale.get()

    def place(self, x, y, width):
        self.label.place(x=x, y=y, width=width, height=20)
        self.scale.place(x=x, y=y+20, width=width, height=20)
        self.tooltip.place(x=x, y=y+40, width=width, height=10)
