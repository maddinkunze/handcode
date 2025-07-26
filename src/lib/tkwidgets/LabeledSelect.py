import typing
import tkinter as tk
from tkinter import font as tkf
from classproperty import classproperty

class SelectOption:
    def __init__(self, id: str|int, name: str|None = None, image: tk.PhotoImage|str|None = None):
        self.id = id
        self._name = name
        self._image = image

    @property
    def name(self) -> str:
        return self._name or str(self.id)
    
    @property
    def has_image(self) -> bool:
        return self._image is not None

    @property
    def image(self) -> tk.PhotoImage|None:
        if isinstance(self._image, str):
            self._image = tk.PhotoImage(file=self._image)
        if isinstance(self._image, tk.PhotoImage):
            return self._image
        return None

    def __repr__(self):
        return f"SelectOption(id={self.id}, name={self.name})"

class LabeledSelect:
    def __init__(self, root, **kwargs):
        self._options = list[SelectOption]()
        self.listeners = dict[str, dict[str, typing.Callable]]()
        self.label = tk.Label(root)
        self.var = tk.StringVar()
        self.select = tk.OptionMenu(root, self.var, "")
        self.select.configure(highlightthickness=0, relief=tk.FLAT, borderwidth=0)
        self.selectmenu.configure(relief=tk.FLAT)
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
            self.selectmenu.configure(**cmenu)

    def setOptions(self, options: list[SelectOption]):
        if self.get() not in options:
            self.set("")

        self._options = options
        self.selectmenu.delete(0, tk.END)
        for option in options:
            _image_data = {}
            if option.has_image:
                _image_data["image"] = option.image
                _image_data["font"] = self._empty_font_lz
            self.selectmenu.add_command(label=option.name, command=lambda _opt=option: self.set(_opt), **_image_data)

    def get(self) -> SelectOption|str:
        value = self.var.get()
        for opt in self._options:
            if opt.name == value:
                return opt
        return value

    def getId(self) -> str:
        value = self.get()
        if isinstance(value, SelectOption):
            return value.id
        return value

    def set(self, value: str|SelectOption, *, noevent=False):
        _prev = self.var.get()
        if isinstance(value, SelectOption):
            value = value.name
        if _prev == value:
            return
        
        if not noevent:
            self._onbeforechange()
        self.var.set(value)
        if not noevent:
            self._onchange()

    def setById(self, id: str, *, force: bool = True, noevent: bool = False):
        for option in self._options:
            if option.id != id:
                continue
            self.set(option, noevent=noevent)
            return
        self.set(id, noevent=noevent)

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

    _empty_font_lz = None
    @classproperty
    def _empty_font(cls):
        if cls._empty_font_lz is None:
            cls._empty_font_lz = tkf.Font(size=0)
        return cls._empty_font_lz
    
    @property
    def selectmenu(self) -> tk.Menu:
        return self.select["menu"]
