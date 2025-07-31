import .prestart as prestart # type: ignore
prestart.unpack_relevant_files()

import os
import re
import sys
import json
import time
import queue
import random
import legacy # type: ignore
import typing
import threading
import traceback
import webbrowser
import dataclasses
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb

from common import path_data, path_settings, set_tk_icon, version_handcode
if typing.TYPE_CHECKING:
    import lib.tkwidgets as tkw
else:
    import tkwidgets as tkw # type: ignore

tkm = tk
if sys.platform == "darwin":
    import tkmacosx as tkm # type: ignore

T = typing.TypeVar("T")

# This is just the GUI for this program, dont be intimidated.
# For the main part of the program have a look at the HandGCode class in the src/lib/handwriting/gcode.py file

class HandCodeApp:
    VERSION_SETTINGS_HANDCODE = version_handcode
    STYLE = {
      "bg_window": "#303030",
      "bg_button": "#505050",
      "bg_button_hover": "#404040",
      "bg_button_start": "#409040",
      "bg_button_start_hover": "#50A050",
      "bg_scroll": "#202020",
      "bg_inner": "#101010",
      "bg_separator": "#606060",
      "fg_button": "#D0D0D0",
      "fg_button_hover": "#D0D0D0",
      "fg_button_start": "#004000",
      "fg_button_start_hover": "#004000",
      "fg_scroll": "#808080",
      "fg_label": "#D0D0D0",
      "fg_text": "#F0F0F0",
      "fg_hint": "#A0A0A0",
      "fg_progress": "#409040",
      "relief": "flat",
      "borderwidth": 0,
      "highlightthickness": 0,
    }

    _MAP_FILETYPES = {
        "gcode": "GCode",
        "svg": "SVG",
    }

    def _load_fonts(self) -> None:
        _font_tooltip_size = 7
        if sys.platform == "linux":
            _font_tooltip_size = 6
        self._font_tooltip = tkf.Font(size=_font_tooltip_size)

        _font_text_size = 9
        if sys.platform == "linux":
            _font_text_size = 8
        self._font_text = tkf.Font(size=_font_text_size)
        
        _font_entry_size = 12
        if sys.platform == "win32":
            _font_entry_size = 10
        if sys.platform == "linux":
            _font_entry_size = 10
        self._font_entry = tkf.Font(size=_font_entry_size)

        _font_label_size = 10
        if sys.platform == "linux":
            _font_label_size = 9
        self._font_label = tkf.Font(size=_font_label_size, weight="bold")

        self._font_start = tkf.Font(size=24, weight="bold")

    def _load_styles(self) -> None:
        self._style_window = {
            "bg": self.STYLE["bg_window"],
        }

        self._style_frame = {
            "bg": self.STYLE["bg_window"],
            "bd": self.STYLE["borderwidth"],
            "relief": tk.FLAT,
        }

        self._style_canvas = {
            "bg": self.STYLE["bg_window"],
            "bd": self.STYLE["borderwidth"],
            "relief": tk.FLAT,
            "highlightthickness": 0,
        }

        _style_label = {
            "bg": self.STYLE["bg_window"],
            "fg": self.STYLE["fg_label"],
            "bd": self.STYLE["borderwidth"],
            "highlightthickness": self.STYLE["highlightthickness"],
        }

        self._style_label_section = {
            **_style_label,
            "font": self._font_label,
        }

        self._style_label_input = {
            **_style_label,
            "font": self._font_text,
        }

        self._style_label_tooltip = {
            **_style_label,
            "font": self._font_tooltip,
        }

        self._style_label_link = {
            **self._style_label_input,
            "fg": "#4286f4",
        }
        if sys.platform == "darwin":
            self._style_label_link["cursor"] = "pointinghand"
        if sys.platform == "win32":
            self._style_label_link["cursor"] = "hand2"
        if sys.platform == "linux":
            self._style_label_link["cursor"] = "hand2"

        self._style_scroll_x = "Maddin.HC.Horizontal.TScrollbar"
        self._style_scroll_y = "Maddin.HC.Vertical.TScrollbar"

        self._style_entry_default = {
            "bg": self.STYLE["bg_inner"],
            "fg": self.STYLE["fg_text"],
            "insertbackground": self.STYLE["fg_hint"],
            "relief": tk.FLAT,
            "bd": self.STYLE["borderwidth"],
            "highlightthickness": self.STYLE["highlightthickness"],
        }

        _style_entry_custom = {
            "bgentry": self.STYLE["bg_inner"],
            "fgentry": self.STYLE["fg_text"],
            "bgcursor": self.STYLE["fg_hint"],
            "font": self._font_entry,
            "fontlabel": self._font_text,
            "relief": tk.FLAT,
            "bd": self.STYLE["borderwidth"],
            "highlightthickness": self.STYLE["highlightthickness"],
        }

        self._style_entry_scrolled = {
            **_style_entry_custom,
            "stylescrollx": self._style_scroll_x,
            "stylescrolly": self._style_scroll_y,
        }

        self._style_entry_unit = {
            **_style_entry_custom,
            "fgunit": self.STYLE["fg_hint"]
        }

        self._style_entry_labeled = {
            **self._style_entry_unit,
            "bglabel": self.STYLE["bg_window"],
            "fglabel": self.STYLE["fg_label"],
        }

        self._style_button_default = {
            "bg": self.STYLE["bg_button"],
            "fg": self.STYLE["fg_button"],
            "activebackground": self.STYLE["bg_button_hover"],
            "activeforeground": self.STYLE["fg_button_hover"],
            "relief": tk.FLAT,
            "bd": self.STYLE["borderwidth"],
            "highlightthickness": self.STYLE["highlightthickness"],
        }

        self._style_button_start = {
            "font": self._font_start,
            "bg": self.STYLE["bg_button_start"],
            "fg": self.STYLE["fg_button_start"],
            "activebackground": self.STYLE["bg_button_start_hover"],
            "activeforeground": self.STYLE["fg_button_start_hover"],
            "relief": tk.FLAT,
            "bd": self.STYLE["borderwidth"],
            "highlightthickness": self.STYLE["highlightthickness"],
        }

        self._style_scale_labeled = {
            "bglabel": self.STYLE["bg_window"],
            "fglabel": self.STYLE["fg_label"],
            "fgtooltip": self.STYLE["fg_hint"],
            "bgscale": self.STYLE["bg_inner"],
            "fgscale": self.STYLE["bg_button"],
            "fgscale:hover": self.STYLE["bg_button_hover"],
            "font": self._font_text,
            "fonttooltip": self._font_tooltip,
            "bd": self.STYLE["borderwidth"],
            "highlightthickness": self.STYLE["highlightthickness"],
        }

        self._style_select_labeled = {
            "bglabel": self.STYLE["bg_window"],
            "fglabel": self.STYLE["fg_label"],
            "font": self._font_entry,
            "fontlabel": self._font_text,
            "bd": self.STYLE["borderwidth"],
            "highlightthickness": self.STYLE["highlightthickness"],
        }

        if sys.platform != "darwin":
            self._style_select_labeled["bgselect"] = self.STYLE["bg_button"],
            self._style_select_labeled["bgselect:hover"] = self.STYLE["bg_button_hover"],
            self._style_select_labeled["fgselect"] = self.STYLE["fg_button"],
            self._style_select_labeled["fgselect:hover"] = self.STYLE["fg_button_hover"],

        self._style_checkbox_default = {
            "bglabel": self.STYLE["bg_window"],
            "bgcheck": self.STYLE["bg_inner"],
            "fg": self.STYLE["fg_label"],
            "font": self._font_text,
            "bd": self.STYLE["borderwidth"],
            "highlightthickness": self.STYLE["highlightthickness"],
        }

        self._style_checkbox_small = {
            **self._style_checkbox_default,
            "font": self._font_tooltip,
        }

        self._style_separator = {
            "bd": 0,
            "bg": self.STYLE["bg_separator"],
        }

        self._style_ttk = ttk.Style()
        self._style_ttk.theme_use("default")
        self._style_ttk.configure("Maddin.HC.Horizontal.TProgressbar", borderwidth=self.STYLE["borderwidth"], troughcolor=self.STYLE["bg_inner"], background=self.STYLE["fg_progress"], troughrelief=self.STYLE["relief"])
        self._style_ttk.configure('Maddin.HC.Horizontal.TScrollbar', troughcolor=self.STYLE["bg_window"], background=self.STYLE["bg_button"], arrowcolor=self.STYLE["fg_hint"], relief=self.STYLE["relief"], troughrelief=self.STYLE["relief"])
        self._style_ttk.map('Maddin.HC.Horizontal.TScrollbar', background=[('pressed', '!disabled', 'active', self.STYLE["bg_button_hover"])])
        self._style_ttk.configure('Maddin.HC.Vertical.TScrollbar', troughcolor=self.STYLE["bg_window"], background=self.STYLE["bg_button"], arrowcolor=self.STYLE["fg_hint"], relief=self.STYLE["relief"], troughrelief=self.STYLE["relief"])
        self._style_ttk.map('Maddin.HC.Vertical.TScrollbar', background=[('pressed', '!disabled', 'active', self.STYLE["bg_button_hover"])])

    def _create_window(self) -> None:
        self.window = tk.Tk()

    def _init_sizes(self) -> None:
        self._xstart = 10
        self._ystart = 5
        self._xmargin = 10
        self._ymargin = 5
        self._widget_height = 20
        self._scroll_width = 15

        self._outline_width = 0
        if sys.platform == "darwin":
            self._outline_width = 2

        self._settings_width = 240
        self._settings_width_outer = self._settings_width + self._scroll_width
        self._inputs_min_width = 420
        self._start_height = 128
        self._inout_height = 45

        self._window_size = (self._inputs_min_width + self._settings_width_outer, 650)

    def _init_window(self) -> None:

        self.window.resizable(True, True)
        self.window.geometry(f"{self._window_size[0]}x{self._window_size[1]}")
        self.window.minsize(*self._window_size)
        self.window.title("HandCode")
        self.window.configure(**self._style_window)

        # Add icon to window/taskbar
        set_tk_icon(self.window)

    def _init_widgets(self) -> None:
        self._frm_inout = tk.Frame(self.window, **self._style_frame)
        self._lbl_file_in = tk.Label(self._frm_inout, text="Input File (opt):", **self._style_label_section)
        self._btn_file_in = tkm.Button(self._frm_inout, text="Open File...", **self._style_button_default)
        self._lbl_file_process = tk.Label(self.window, text="↴   ↱", **{**self._style_label_section, "font": self._font_start})
        self._lbl_file_out = tk.Label(self._frm_inout, text="Output File:", **self._style_label_section)
        self._edt_file_out = tk.Entry(self._frm_inout, **self._style_entry_default)
        self._slt_file_type = tkw.LabeledSelect(self._frm_inout, label="Format", options=[tkw.SelectOption(fid, fname) for fid, fname in self._MAP_FILETYPES.items()], **self._style_select_labeled)

        self._frm_input = tk.Frame(self.window, **self._style_frame)
        self._lbl_input = tk.Label(self._frm_input, text="Input Text:", **self._style_label_section)
        self._edt_input = tkw.ScrolledEntry(self._frm_input, **self._style_entry_scrolled)

        self._frm_log = tk.Frame(self.window, **self._style_frame)
        self._lbl_log = tk.Label(self._frm_log, text="Event Log:", **self._style_label_section)
        self._edt_log = tkw.ScrolledEntry(self._frm_log, **self._style_entry_scrolled)

        self._frm_start = tk.Frame(self.window, **self._style_frame)

        self._prg_loading = ttk.Progressbar(self._frm_start, orient="horizontal", mode="indeterminate", style="Maddin.HC.Horizontal.TProgressbar")
        self._btn_show = tkm.Button(self._frm_start, text="Open input/output folder", **self._style_button_default)
        self._btn_start = tkm.Button(self._frm_start, text="Start", **self._style_button_start, state=tk.DISABLED)


        self._frm_settings_outer = tk.Frame(self.window, **self._style_frame)
        self._cvs_settings = tk.Canvas(self._frm_settings_outer, **self._style_canvas, yscrollincrement=10)
        self._scr_settings = ttk.Scrollbar(self._frm_settings_outer, orient=tk.VERTICAL, command=self._cvs_settings.yview, style=self._style_scroll_y)
        self._frm_settings = tk.Frame(self._frm_settings_outer, **self._style_frame)

        self._frm_settings.bind("<Configure>", lambda e: self._cvs_settings.configure(scrollregion=self._cvs_settings.bbox("all")))
        self._cvs_settings.create_window((0, 0), window=self._frm_settings, anchor=tk.NW)
        self._cvs_settings.configure(yscrollcommand=self._scr_settings.set)


        self._lbl_model = tk.Label(self._frm_settings, text="Model Settings:", **self._style_label_section)
        self._slt_model = tkw.LabeledSelect(self._frm_settings, label="Model", options=[], **self._style_select_labeled, state=tk.DISABLED)
        self._btn_model_info = tkm.Button(self._frm_settings, text="Show Info", **self._style_button_default, state=tk.DISABLED)
        self._lbl_model_license = tk.Label(self._frm_settings, text="⏳ Loading models...", justify=tk.LEFT, **self._style_label_tooltip)

        self._lbl_font = tk.Label(self._frm_settings, text="Font Settings:", **self._style_label_section)
        self._edt_font_size = tkw.LabeledEntry(self._frm_settings, label="Size", unit="mm", **self._style_entry_labeled)
        self._slt_font_style = tkw.LabeledSelect(self._frm_settings, label="Style", options=[], **self._style_select_labeled)
        self._edt_font_bias = tkw.LabeledEntry(self._frm_settings, label="Legibility", unit="%", **self._style_entry_labeled)

        self._edt_font_line_height = tkw.LabeledEntry(self._frm_settings, label="Line Height", unit="mm", **self._style_entry_labeled)
        self._lbl_font_word_spacing = tk.Label(self._frm_settings, text="Word Spacing", **self._style_label_input)
        self._edt_font_word_spacing = tkw.UnitEntry(self._frm_settings, unit="mm", **self._style_entry_unit)
        self._lbl_font_word_spacing_var = tk.Label(self._frm_settings, text="±", **self._style_label_input)
        self._edt_font_word_spacing_var = tkw.UnitEntry(self._frm_settings, unit="mm", **self._style_entry_unit)

        if sys.platform == "win32":
            label_lhr = "Recalc on f..."
            label_wsr = "Recalc on font s..."
        elif sys.platform == "darwin":
            label_lhr = "Recalc on font..."
            label_wsr = "Recalc on font size change"
        else:
            label_lhr = "Recalc on font s..."
            label_wsr = "Recalc on font size change"
        self._chk_font_line_height_recalc = tkw.Checkbox(self._frm_settings, label=label_lhr, **self._style_checkbox_small)
        self._chk_font_word_spacing_recalc = tkw.Checkbox(self._frm_settings, label=label_wsr, **self._style_checkbox_small)

        if sys.platform == "win32":
            desc_horizontal = "Left      Center    Right"
            desc_vertical = "Top      Center  Bottom"
        elif sys.platform == "darwin":
            desc_horizontal = "Left           Center         Right"
            desc_vertical = "Top          Center        Bottom"
        else:
            desc_horizontal = "Left      Center    Right"
            desc_vertical = "Top      Center  Bottom"
        self._scl_font_align_horizontal = tkw.LabeledScale(self._frm_settings, label="Horzontal Align", description=desc_horizontal, start=0, end=1, step=0.1, **self._style_scale_labeled, state=tk.DISABLED)
        self._scl_font_align_vertical = tkw.LabeledScale(self._frm_settings, label="Vertical Align", description=desc_vertical, start=0, end=1, step=0.1, **self._style_scale_labeled)

        self._lbl_pen = tk.Label(self._frm_settings, text="Pen Settings:", **self._style_label_section)
        self._edt_pen_z_draw = tkw.LabeledEntry(self._frm_settings, label="Z Draw", unit="mm", **self._style_entry_labeled)
        self._edt_pen_z_travel = tkw.LabeledEntry(self._frm_settings, label="Z Travel", unit="mm", **self._style_entry_labeled)
        self._edt_pen_z_pause = tkw.LabeledEntry(self._frm_settings, label="Z Pause", unit="mm", **self._style_entry_labeled)

        self._edt_pen_f_draw = tkw.LabeledEntry(self._frm_settings, label="Feedrate Draw", unit="mm/min", **self._style_entry_labeled)
        self._edt_pen_f_travel = tkw.LabeledEntry(self._frm_settings, label="Feedrate Travel", unit="mm/min", **self._style_entry_labeled)


        self._lbl_page = tk.Label(self._frm_settings, text="Page Settings:", **self._style_label_section)
        self._edt_page_width = tkw.LabeledEntry(self._frm_settings, label="Width (o≃∞)", unit="mm", **self._style_entry_labeled)
        self._edt_page_height = tkw.LabeledEntry(self._frm_settings, label="Height (o≃∞)", unit="mm", **self._style_entry_labeled)
        self._edt_page_rotation = tkw.LabeledEntry(self._frm_settings, label="Rotation", unit="°", **self._style_entry_labeled)

        self._lbl_other = tk.Label(self._frm_settings, text="Other Features:", **self._style_label_section)
        self._chk_feature_replace = tkw.Checkbox(self._frm_settings, label="Replace unknown characters", **self._style_checkbox_default)
        self._lbl_feature_replace = tk.Label(self._frm_settings, text="(e.g. ä -> a, Q -> O)", **self._style_label_tooltip)
        self._chk_feature_imitate = tkw.Checkbox(self._frm_settings, label="Imitate some unknown characters", **self._style_checkbox_default)
        self._chk_feature_imitate_dam = tkw.Checkbox(self._frm_settings, label="Imitate diaresis as macron (ä -> ā)", **self._style_checkbox_small)
        self._chk_feature_split_pages = tkw.Checkbox(self._frm_settings, label="One output file for each page", **self._style_checkbox_default)


        self._seg_left_right = tk.Frame(self.window, **self._style_separator)

    def _update_entire_layout(self) -> None:
        self._update_trivial_layout()
        self._update_settings_layout()
        self._update_non_trivial_sizes()

    def _update_trivial_layout(self) -> None:
        x = self._xstart
        y = self._ystart

        self._lbl_file_in.place(x=x, y=y, height=self._widget_height)
        self._btn_file_in.place(x=x-self._outline_width, y=y+self._widget_height-self._outline_width, width=120+2*self._outline_width, height=self._widget_height+2*self._outline_width)
        x += 120
        if sys.platform == "win32":
            self._lbl_file_process.place(x=x, y=y+self._widget_height-2)
        elif sys.platform == "darwin":
            self._lbl_file_process.place(x=x+5, y=y+self._widget_height+1)
        else:
            self._lbl_file_process.place(x=x, y=y+self._widget_height)
        self._lbl_file_process.tkraise(self._frm_input)
        x += 70
        self._lbl_file_out.place(x=x, y=y, height=self._widget_height)
        self._edt_file_out.place(x=x, y=y+self._widget_height, width=120, height=self._widget_height)
        x += 120 + self._xmargin
        self._slt_file_type.place(x=x, y=y, width=80)

        x = self._xstart
        y = self._ystart
        self._lbl_input.place(x=x, y=y, height=self._widget_height)

        y += self._widget_height
        self._edt_input.place(x=x, y=y, relwidth=1, relheight=1, width=-2*self._xmargin, height=-self._ymargin-self._widget_height)

        x = self._xstart
        y = self._ystart
        self._lbl_log.place(x=x, y=y, height=self._widget_height)

        y += self._widget_height
        self._edt_log.place(x=x, y=y, relwidth=1, relheight=1, width=-2*self._xmargin, height=-3*self._ymargin-self._widget_height)

        x = self._xstart
        y = self._ystart
        self._prg_loading.place(x=x, y=y, width=235, height=self._widget_height)
        y += self._widget_height + self._ymargin + 2
        self._btn_show.place(x=x-self._outline_width, y=y-self._outline_width, width=235+2*self._outline_width, height=self._widget_height+self._ymargin+2*self._outline_width)
        y += self._widget_height + 3 * self._ymargin
        self._btn_start.place(x=x-self._outline_width, y=y-self._outline_width, width=235+2*self._outline_width, height=2*self._widget_height+2*self._ymargin+2*self._outline_width)

    def _update_settings_layout(self) -> None:
        xstart = self._xmargin

        x = xstart
        y = self._ystart
        self._lbl_model.place(x=x, y=y, height=self._widget_height)
        y += self._widget_height
        self._slt_model.place(x=x, y=y, width=130)
        x += 130 + self._xmargin
        self._btn_model_info.place(x=x-self._outline_width, y=y+self._widget_height-self._outline_width, width=80+2*self._outline_width, height=self._widget_height+2*self._outline_width)

        x = xstart
        y += 2*self._widget_height + 3
        self._lbl_model_license.place(x=x, y=y, height=self._widget_height)
        y += self._widget_height + self._ymargin

        self._lbl_font.place(x=x, y=y, height=self._widget_height)

        y += self._widget_height
        self._edt_font_size.place(x=x, y=y, width=60)
        x += 60 + self._xmargin
        self._slt_font_style.place(x=x, y=y, width=80)
        x += 80 + self._xmargin
        self._edt_font_bias.place(x=x, y=y, width=60)

        x = xstart
        y += 2 * self._widget_height + self._ymargin
        self._edt_font_line_height.place(x=x, y=y, width=80)
        x += 80 + self._xmargin
        self._lbl_font_word_spacing.place(x=x, y=y, width=100, height=self._widget_height)
        y += self._widget_height
        self._edt_font_word_spacing.place(x=x, y=y, width=65)
        x += 65
        self._lbl_font_word_spacing_var.place(x=x, y=y, width=15, height=self._widget_height)
        x += 15
        self._edt_font_word_spacing_var.place(x=x, y=y, width=50)

        x = xstart
        y += self._widget_height
        self._chk_font_line_height_recalc.place(x=x, y=y, height=self._widget_height)
        x += 80 + self._xmargin
        self._chk_font_word_spacing_recalc.place(x=x, y=y, height=self._widget_height)

        x = xstart
        y += self._widget_height + self._ymargin
        self._scl_font_align_horizontal.place(x=x, y=y, width=105)
        x += 105 + self._xmargin
        self._scl_font_align_vertical.place(x=x, y=y, width=105)

        x = xstart
        y += 2 * self._widget_height + 10 + 3 * self._ymargin  # + 10 since the LabeledScale is 10px larger than 2 * height
        self._lbl_pen.place(x=x, y=y, height=self._widget_height)

        x = xstart
        y += self._widget_height
        self._edt_pen_z_draw.place(x=x, y=y, width=67)
        x += 67 + self._xmargin
        self._edt_pen_z_travel.place(x=x, y=y, width=66)
        x += 66 + self._xmargin
        self._edt_pen_z_pause.place(x=x, y=y, width=67)

        x = xstart
        y += 2 * self._widget_height + self._ymargin
        self._edt_pen_f_draw.place(x=x, y=y, width=105)
        x += 105 + self._xmargin
        self._edt_pen_f_travel.place(x=x, y=y, width=105)

        x = xstart
        y += 2 * self._widget_height + 3 * self._ymargin
        self._lbl_page.place(x=x, y=y, height=self._widget_height)

        x = xstart
        y += self._widget_height
        self._edt_page_width.place(x=x, y=y, width=75)
        x += 75 + self._xmargin
        self._edt_page_height.place(x=x, y=y, width=75)
        x += 75 + self._xmargin
        self._edt_page_rotation.place(x=x, y=y, width=50)

        x = xstart
        y += 2 * self._widget_height + 3 * self._ymargin
        self._lbl_other.place(x=x, y=y, height=self._widget_height)

        x = xstart
        y += self._widget_height
        self._chk_feature_replace.place(x=x, y=y, height=self._widget_height)

        x = xstart + self._widget_height
        y += self._widget_height
        self._lbl_feature_replace.place(x=x, y=y, height=self._widget_height//2)

        x = xstart
        y += self._widget_height//2 + self._ymargin
        self._chk_feature_imitate.place(x=x, y=y, height=self._widget_height)

        x = xstart + self._widget_height
        y += self._widget_height
        self._chk_feature_imitate_dam.place(x=x, y=y, height=self._widget_height-5)

        x = xstart
        y += self._widget_height + self._ymargin
        self._chk_feature_split_pages.place(x=x, y=y, height=self._widget_height)

        height = y + self._widget_height
        self._frm_settings.configure(width=self._settings_width, height=height)

    def _update_non_trivial_sizes(self) -> None:
        self._frm_inout.place(x=0, y=0, width=-self._settings_width_outer, height=self._inout_height, relwidth=1)
        self._frm_input.place(x=0, y=self._inout_height, width=-self._settings_width_outer, height=-self._inout_height/2, relwidth=1, relheight=0.7)
        self._frm_log.place(x=0, y=self._inout_height/2, width=-self._settings_width_outer, height=-self._inout_height/2, rely=0.7, relwidth=1, relheight=0.3)
        self._frm_settings_outer.place(x=0, y=0, width=self._settings_width_outer, height=-self._start_height, relheight=1, relx=1, rely=0, anchor=tk.NE)
        self._cvs_settings.place(x=0, y=0, relwidth=1, width=-self._scroll_width, relheight=1)
        self._scr_settings.place(x=0, y=0, width=self._scroll_width, relx=1, relheight=1, anchor=tk.NE)
        self._frm_start.place(x=0, y=0, width=self._settings_width_outer, height=self._start_height, relx=1, rely=1, anchor=tk.SE)
        self._seg_left_right.place(x=-self._settings_width_outer+1, y=self._ymargin, width=2, height=-2*self._ymargin, relx=1, rely=0, anchor=tk.NE, relheight=1)

    def _init_handlers(self) -> None:
        self._slt_model.addListener("change", self._switch_model)
        self._btn_model_info.configure(command=self._show_model_info)

        self._edt_font_size.addListener("change", self._recalculate_font_sizes)
        self._edt_font_line_height.addListener("change", self._recalculate_font_factors)
        self._edt_font_word_spacing.addListener("change", self._recalculate_font_factors)
        self._edt_font_word_spacing_var.addListener("change", self._recalculate_font_factors)
        self._chk_font_line_height_recalc.addListener("change", self._recalculate_font_factors)
        self._chk_font_word_spacing_recalc.addListener("change", self._recalculate_font_factors)

        self._chk_feature_imitate.addListener("change", self._update_feature_imitate)

        self._frm_settings_outer.bind_all("<MouseWheel>", self._scroll_settings_wheel, add=True)
        self._frm_settings_outer.bind_all("<Button-4>", self._scroll_settings_buttons, add=True)
        self._frm_settings_outer.bind_all("<Button-5>", self._scroll_settings_buttons, add=True)

        self._btn_file_in.configure(command=self._select_input_file)
        self._btn_show.configure(command=self._show_folder)
        self._btn_start.configure(command=self.start_convert)

    def _scroll_settings_wheel(self, event: tk.Event):
        if not str(event.widget).startswith(str(self._frm_settings_outer)):
            # bit of a hack to check if the event occured on a widget that is a child of the settings frame
            return
        
        if event.delta == 0:
            return
        
        # avoid flickering when continuing to scroll down when already at the bottom
        if self._cvs_settings.yview()[1] >= 1:
            if (event.delta > 0) and self._settings_was_scrolling_down:
                self._settings_was_scrolling_down = False
                return
            elif event.delta < 0:
                self._settings_was_scrolling_down = True
            else:
                self._settings_was_scrolling_down = False
        else:
            self._settings_was_scrolling_down = False
        
        y_steps = int(-event.delta/abs(event.delta))
        self._cvs_settings.yview_scroll(y_steps, tk.UNITS)
 
    def _scroll_settings_buttons(self, event: tk.Event):
        if not str(event.widget).startswith(str(self._frm_settings_outer)):
            # bit of a hack to check if the event occured on a widget that is a child of the settings frame
            return
        
        y_steps = 1
        if event.num == 4:
            y_steps *= -1
        self._cvs_settings.yview_scroll(y_steps, tk.UNITS)

    def _init_state_vars(self) -> None:
        self._font_factors = dict[str, float]()
        self._ui_queue = queue.Queue[typing.Callable[[], typing.Any]]()
        self._ui_poll_tries = 5 # number of callbacks to call at most during one ui update run
        self._ui_poll_interval = 100
        self._convert_queue = queue.Queue[str]()

        @dataclasses.dataclass
        class _ProgressData:
            description: str|None
            value: int|float|None
            maximum: int|float|None
            was_update_requested: bool
            is_animation_stopped: bool
            @property
            def is_stopped(self):
                return (self.description is None) and (self.value is None) and (self.maximum is None)
            def mark_stopped(self):
                self.description = None
                self.value = None
                self.maximum = None
        self._progress_data = _ProgressData(description=None, value=None, maximum=None, was_update_requested=False, is_animation_stopped=False)

        self._pen_settings_generators = dict[str, typing.Callable]()
        self._convert_settings = dict[str, typing.Any]()
        self._convert_data = dict[str, typing.Any]()
        self._re_font_style = re.compile(r"^\s*Style (\d+)\s*$")
        self._gcode = None
        self._last_successful_model = None

        self._settings_was_scrolling_down = False

    def _switch_model(self) -> None:
        model = self._slt_model.getId()
        if not model:
            return
        
        self._read_model_setting_from_ui()
        self._slt_model.configure(state=tk.DISABLED)
        self._btn_model_info.configure(state=tk.DISABLED)
        self._lbl_model_license.configure(text="⏳ Loading model...")
        self._report("log", f"Switching to model: {model}\n")
        self._convert_queue.put("model")

    def _get_font_size(self, entry) -> float:
        try:
            return float(entry.get().strip())
        except Exception:
            return -1

    def _recalculate_font_size(self, base: float, entry: tk.Entry, name: str, digits: int=-1) -> None:
        if name not in self._font_factors:
            return
        template = "{size}"
        if digits > 0:
            template = f"{{size:.0{digits}f}}"
        size = base * self._font_factors[name]
        entry.set(template.format(size=size).rstrip("0").rstrip("."))

    def _recalculate_font_sizes(self):
        font_size = self._get_font_size(self._edt_font_size)
        if font_size <= 0:
            return
        
        if self._chk_font_line_height_recalc.get():
            self._recalculate_font_size(font_size, self._edt_font_line_height, "lineheight", digits=4)
        if self._chk_font_word_spacing_recalc.get():
            self._recalculate_font_size(font_size, self._edt_font_word_spacing, "wordspacing", digits=2)
            self._recalculate_font_size(font_size, self._edt_font_word_spacing_var, "wordspacingvar", digits=1)

    def _recalculate_font_factor(self, base: float, entry: tk.Entry, name: str) -> None:
        size = self._get_font_size(entry)
        self._font_factors[name] = size/base

    def _recalculate_font_factors(self):
        font_size = self._get_font_size(self._edt_font_size)
        if font_size <= 0:
            return
        
        if self._chk_font_line_height_recalc.get():
            self._recalculate_font_factor(font_size, self._edt_font_line_height, "lineheight")
        else:
            self._font_factors.pop("lineheight", None)
        if self._chk_font_word_spacing_recalc.get():
            self._recalculate_font_factor(font_size, self._edt_font_word_spacing, "wordspacing")
            self._recalculate_font_factor(font_size, self._edt_font_word_spacing_var, "wordspacingvar")
        else:
            self._font_factors.pop("wordspacing", None)
            self._font_factors.pop("wordspacingvar", None)

    def _show_model_info(self):
        window = tk.Toplevel(self.window, **self._style_window)
        window.title("Model Info")

        lbl_title = tk.Label(window, text=f"Model Name: {self._gcode._model.name} ({self._gcode._model.id})", **self._style_label_section)

        lbl_info = tk.Label(window, text="Description:", **self._style_label_input)
        edt_info = tkw.ScrolledEntry(window, tk.WORD, **self._style_entry_scrolled)
        edt_info.set(self._gcode._model.description)

        lbl_license = tk.Label(window, text="License:", **self._style_label_input)
        edt_license = tkw.ScrolledEntry(window, tk.WORD, **self._style_entry_scrolled)
        edt_license.set(self._gcode._model.license)

        lbls_url = list[tk.Label]()
        for desc, url in self._gcode._model.urls:
            lbl_url = tk.Label(window, text=f"{desc} ↗", **self._style_label_link)
            lbl_url.bind("<Button-1>", lambda _, _url=url: webbrowser.open_new_tab(_url))
            lbls_url.append(lbl_url)

        btn_close = tkm.Button(window, text="Close", **self._style_button_default, command=lambda *_: window.destroy())

        height_urls = len(lbls_url) * 20
        height_other = 105

        lbl_title.place(x=5, y=5, relwidth=1, height=20, width=-10)
        lbl_info.place(x=5, y=25, height=20)
        edt_info.place(x=5, y=45, height=-(height_other+height_urls)/2, relheight=0.5, relwidth=1, width=-10)
        lbl_license.place(x=5, y=50-(height_other+height_urls)/2, rely=0.5)
        edt_license.place(x=5, y=70-(height_other+height_urls)/2, rely=0.5, relwidth=1, width=-10, relheight=0.5, height=-(height_other+height_urls)/2)
        for i, lbl in enumerate(lbls_url):
            lbl.place(x=5, y=-height_urls-30+i*20, rely=1, height=20)
        btn_close.place(x=-5, y=-5, relx=1, rely=1, width=100, height=20, anchor=tk.SE)

        window_size = (500, height_urls+height_other+2*180)
        window.minsize(*window_size)
        window.geometry("x".join(map(str, window_size)))

    def _update_feature_imitate(self):
        state = tk.NORMAL if self._chk_feature_imitate.get() else tk.DISABLED
        self._chk_feature_imitate_dam.configure(state=state)

    def _select_input_file(self):
        filename = tkfd.askopenfilename(title="Open text file...", initialdir=path_data)
        if not filename:
            self._report("log", "No file selected!\n")
            return
        self._read_input_file(filename)

    def _read_input_file(self, filename):
        if not filename:
            return
        
        file = None
        try:
            file = open(filename, "r")
            self._edt_input.set(file.read())
        except Exception as e:
            self._report("log", f"Unknown error reading file: {e}")
        finally:
            if file:
                file.close()

    def _show_folder(self):
        if sys.platform == "win32":
            os.startfile(path_data)
            return

        path_data_safe = path_data.replace('"', r'\"')
        if sys.platform.startswith("linux"):
            os.system(f"xdg-open \"{path_data_safe}\"")
            return

        if sys.platform == "darwin":
            os.system(f"open \"{path_data_safe}\"")
            return


    def _update_ui_queue(self):
        for _ in range(self._ui_poll_tries):
            try:
                cb = self._ui_queue.get(block=False)
                cb()
            except queue.Empty:
                break
            except Exception as e:
                tkmb.showerror("Error in the UI polling loop", f"The following unhandled exception occured: {e}\n\n{traceback.format_exc()}\n\n{sys.exc_info()}")

        self.window.update()
        self._schedule_ui_update()

    def _schedule_ui_update(self):
        self.window.after(self._ui_poll_interval, self._update_ui_queue)

    def start_convert(self):
        if self._convert_queue.qsize() > 0:
            return
        
        self._btn_start.configure(state=tk.DISABLED)
        self._edt_log.set("")
        self._prg_loading.start()

        self._read_settings_from_ui()
        if not self.is_test_start_behaviour:
            self._save_settings_to_file()

        errors = self._convert_settings_to_data()
        if errors:
            self._report("log", f"\n{errors} errors were encountered while parsing your current settings. Please see above for more information.\n")
            self._prg_loading.stop()
            return
        
        self._convert_queue.put("generate")

    @property
    def is_test_start_behaviour(self) -> bool:
        return "--test-start-behaviour" in sys.argv

    def _report(self, event, data=None):
        if (event == "log") and data:
            self._edt_log.append(data)

        if (event == "libraries_loaded"):
            models = [tkw.SelectOption(mid, model.name) for mid, model in self._gcode.all_models.items()]
            self._slt_model.configure(options=models)
            self._write_model_setting_to_ui()

        if (event == "model_loaded"):
            self._slt_model.configure(state=tk.NORMAL)
            self._btn_model_info.configure(state=tk.NORMAL)
            self._lbl_model_license.configure(text=self._gcode._model.short_info)
            self._last_successful_model = self._slt_model.getId()
            self._write_settings_to_ui()

        if (event == "model_failed"):
            self._report("log", "Switching back to last known working model\n")
            self._slt_model.setById(self._last_successful_model)

        if (event == "success"):
            self._btn_start.configure(state=tk.NORMAL)
            self._progress_data.mark_stopped()
            self._report("progress")

        if (event == "error"):
            self._btn_start.configure(state=tk.NORMAL)
            self._progress_data.mark_stopped()
            self._report("progress")
            self._report("log", f"\nUnhandled error: {data}\n")
            try:
                print(f"An error occurred:\n{traceback.format_exception(data)}\n\n{sys.exc_info()}")
            except Exception:
                print(f"An error occurred:\n{traceback.format_exc()}\n\n{sys.exc_info()}")

        if (event == "critical"):
            tkmb.showerror("Error in the neural network thread", data)

        if (event == "progress"):
            self._progress_data.was_update_requested = False
            if (self._progress_data.is_stopped):
                self._prg_loading.configure(mode="indeterminate")
                self._prg_loading.stop()
                self._progress_data.is_animation_stopped = True
            elif self._progress_data.maximum is not None:
                if not self._progress_data.is_animation_stopped:
                    self._prg_loading.stop()
                self._prg_loading.configure(mode="determinate", value=self._progress_data.value or 0, maximum=self._progress_data.maximum)
                self._progress_data.is_animation_stopped = True
            else:
                self._prg_loading.configure(mode="indeterminate")
                self._prg_loading.start()
                self._progress_data.is_animation_stopped = False

    def _report_thread_safe(self, event, data=None):
        self._ui_queue.put(lambda: self._report(event, data=data))

    def _update_progress_bar(self, description: str|None, value: int|float|None, maximum: int|float|None):
        has_mode_changed = (self._progress_data.description != description) or ((maximum is None) != (self._progress_data.maximum is None))

        if (description is not None) or ((value is None) and (maximum is None)):
            self._progress_data.description = description

        if maximum:
            add_for_start_pos = maximum / 25
            value = (value or 0) + add_for_start_pos
            maximum = maximum + add_for_start_pos
        self._progress_data.value = value
        self._progress_data.maximum = maximum

        if self._progress_data.was_update_requested or not has_mode_changed:
            return
        
        self._report_thread_safe("progress")

    def _log_thread_safe(self, text: str):
        self._report_thread_safe("log", text)

    def _thread_convert(self):
        try:
            self._log_thread_safe("Loading framework... ")
            if typing.TYPE_CHECKING:
                import lib.handwriting as handwriting
            else:
                import handwriting # type: ignore
            gcode = handwriting.gcode.HandGCode(logger=self._log_thread_safe, progress=self._update_progress_bar)
            self._gcode = gcode
            self._report_thread_safe("libraries_loaded")

            self._log_thread_safe("Done\nLoading helper functions... ")
            self._pen_settings_generators["gcode"] = handwriting.commands.gcode
            self._pen_settings_generators["svg"] = handwriting.commands.svg

            self._log_thread_safe("Done\n")
            self._report_thread_safe("success")

            if self.is_test_start_behaviour:
                threading.Thread(target=self._thread_test_start_behaviour).start()

            while True:
                task = self._convert_queue.get()
 
                if task == "stop":
                    return

                if task == "model":
                    try:
                        self._log_thread_safe("Loading model... ")
                        gcode.switch_model(self._slt_model.getId())
                        self._log_thread_safe("Done\n\n")
                        self._report_thread_safe("model_loaded")
                    except Exception as e:
                        self._log_thread_safe("Failed\nSee below and in your terminal (if available) for more info\n")
                        self._report_thread_safe("error", e)
                        self._log_thread_safe("\n")
                        self._report_thread_safe("model_failed")

                if task == "generate":
                    try:
                        gcode.generate(self._convert_data)
                        self._report_thread_safe("success")
                    except Exception as e:
                        self._report_thread_safe("error", e)

                self._convert_queue.task_done()
        
        except Exception as e:
            self._report_thread_safe("critical", f"The following unhandled exception occured: {e}\n\n{traceback.format_exc()}\n\n{sys.exc_info()}")

    def _thread_test_start_behaviour(self):
        time.sleep(3)
        self.window.after(0, lambda *_: self._edt_input.insert(0, "Hello World"))
        time.sleep(1)
        self.start_convert()
        time.sleep(30)
        self.window.after(0, self.window.destroy)

    @staticmethod
    def _save_path_in_dict(d, path, value):
        plen = len(path)
        for i, p in enumerate(path, 1):
            if i < plen:
                if p not in d:
                    d[p] = {}
                d = d[p]
                continue
            d[p] = value

    def _save_setting(self, path, value):
        self._save_path_in_dict(self._convert_settings, path, value)

    def _read_settings_from_ui(self):
        self._convert_settings.clear()
        self._convert_settings["version"] = version_handcode

        self._read_model_setting_from_ui()

        self._save_setting(["input", "text"], self._edt_input.get())
        self._save_setting(["output", "file"], self._edt_file_out.get())
        self._save_setting(["output", "format"], self._slt_file_type.getId())

        self._save_setting(["font", "size"], self._edt_font_size.get())
        self._save_setting(["font", "style"], self._slt_font_style.getId())
        self._save_setting(["font", "bias"], self._edt_font_bias.get())
        self._save_setting(["font", "lineheight"], self._edt_font_line_height.get())
        self._save_setting(["font", "wordspacing"], self._edt_font_word_spacing.get())
        self._save_setting(["font", "wordspacingvariance"], self._edt_font_word_spacing_var.get())
        #self._save_setting(["font", "align", "horizontal"], self._scl_font_align_horizontal.get())
        self._save_setting(["font", "align", "vertical"], self._scl_font_align_vertical.get())

        self._save_setting(["pen", "heights", "draw"], self._edt_pen_z_draw.get())
        self._save_setting(["pen", "heights", "travel"], self._edt_pen_z_travel.get())
        self._save_setting(["pen", "heights", "pause"], self._edt_pen_z_pause.get())
        self._save_setting(["pen", "speeds", "draw"], self._edt_pen_f_draw.get())
        self._save_setting(["pen", "speeds", "travel"], self._edt_pen_f_travel.get())

        self._save_setting(["page", "width"], self._edt_page_width.get())
        self._save_setting(["page", "height"], self._edt_page_height.get())
        self._save_setting(["page", "rotate"], self._edt_page_rotation.get())

        self._save_setting(["features", "replace", "enabled"], self._chk_feature_replace.get())
        self._save_setting(["features", "imitate", "enabled"], self._chk_feature_imitate.get())
        self._save_setting(["features", "imitate", "diaresisasmacron"], self._chk_feature_imitate_dam.get())
        self._save_setting(["features", "splitpages", "enabled"], self._chk_feature_split_pages.get())

    def _read_model_setting_from_ui(self):
        self._save_setting(["model", "name"], self._slt_model.getId())

    def _write_settings_to_ui(self) -> None:
        format_float = legacy.formatFloat
        format_font_style_name = legacy.formatFontStyleName

        self._edt_input.set(self._convert_settings.get("input", {}).get("text", ""))
        self._edt_file_out.delete(0, tk.END)
        self._edt_file_out.insert(0, self._convert_settings.get("output", {}).get("file", "demo.nc"))
        self._slt_file_type.setById(self._convert_settings.get("output", {}).get("format", "gcode"))

        self._write_model_setting_to_ui(noevent=True)

        settings_font = self._convert_settings.get("font", {})
        font_size = settings_font.get("size", format_float(10))
        try:
            font_size = float(font_size)
        except (ValueError, TypeError):
            font_size = 10
        self._edt_font_size.set(font_size)

        font_styles = [tkw.SelectOption(style.id, style.name, style.image_path) for style in self._gcode.writing_styles]
        self._slt_font_style.configure(options=font_styles)
        _default_font_style = font_styles[0]
        font_style_id = settings_font.get("style", _default_font_style)
        if not any(map(lambda f: f.id == font_style_id, font_styles)):
            self._report("log", f"Could not load font style ({font_style_id}) from settings, falling back to {_default_font_style.name}\n")
            font_style_id = _default_font_style.id
        self._slt_font_style.setById(font_style_id)

        self._edt_font_bias.set(settings_font.get("bias", format_float(75)))
        self._edt_font_line_height.set(settings_font.get("lineheight", font_size))
        self._edt_font_word_spacing.set(settings_font.get("wordspacing", format_float(round(font_size * 0.4, 2))))
        self._edt_font_word_spacing_var.set(settings_font.get("wordspacingvariance", format_float(round(font_size * 0.2, 1))))
        self._chk_font_line_height_recalc.set(settings_font.get("lineheight_recalc", True))
        self._chk_font_word_spacing_recalc.set(settings_font.get("wordspacing_recalc", True))
        self._recalculate_font_factors()

        settings_font_align = settings_font.get("align", {})
        self._scl_font_align_horizontal.set(settings_font_align.get("horizontal", 0))
        self._scl_font_align_vertical.set(settings_font_align.get("vertical", 0.8))

        settings_pen = self._convert_settings.get("pen", {})
        settings_pen_heights = settings_pen.get("heights", {})
        self._edt_pen_z_draw.set(settings_pen_heights.get("draw", format_float(0)))
        self._edt_pen_z_travel.set(settings_pen_heights.get("travel", format_float(5)))
        self._edt_pen_z_pause.set(settings_pen_heights.get("pause", format_float(30)))
        settings_pen_speeds = settings_pen.get("speeds", {})
        self._edt_pen_f_draw.set(settings_pen_speeds.get("draw", format_float(1000)))
        self._edt_pen_f_travel.set(settings_pen_speeds.get("draw", format_float(1000)))

        settings_page = self._convert_settings.get("page", {})
        self._edt_page_width.set(settings_page.get("width", format_float(0)))
        self._edt_page_height.set(settings_page.get("height", format_float(0)))
        self._edt_page_rotation.set(settings_page.get("rotate", format_float(0)))

        settings_features = self._convert_settings.get("features", {})
        self._chk_feature_replace.set(settings_features.get("replace", {}).get("enabled", True))
        self._chk_feature_imitate.set(settings_features.get("imitate", {}).get("enabled", True))
        self._update_feature_imitate()
        self._chk_feature_imitate_dam.set(settings_features.get("imitate", {}).get("diaresisasmacron", False))
        self._chk_feature_split_pages.set(settings_features.get("splitpages", {}).get("enabled", False))

    def _write_model_setting_to_ui(self, *, noevent: bool=False) -> None:
        self._slt_model.setById(self._convert_settings.get("model", {}).get("name", "cai-ulw"), noevent=noevent)

    def _parse_font_style(self, style_name: str) -> int:
        try:
            for style in self._gcode.writing_styles:
                if style.name != style_name:
                    continue
                return style.id
            raise ValueError("Invalid writing style")
        except (KeyError, ValueError):
            self._log_thread_safe(f"Invalid writing style selected: \"{style_name}\"\n")
            raise
        except Exception as e:
            self._log_thread_safe(f"Unknown error while parsing writing style \"{style_name}\": {e}\n")
            raise

    def _parse_pen_settings(self, mode, **kwargs):
        if not self._pen_settings_generators:
            raise NotImplementedError("The handwriting library does not seem to have been fully loaded yet!")
        if mode not in self._pen_settings_generators:
            raise NotImplementedError("The mode you requested does not seem to be implemented (yet?).")
        return self._pen_settings_generators[mode](**kwargs)
    
    def _get_convert_setting(self, path: list[str], dtype: typing.Callable[[typing.Any], T]|None=None, default: T|None=None) -> T:
        # Find value in recursive settings dict (as given by path)
        value = self._convert_settings
        for p in path:
            if p not in value:
                self._log_thread_safe(f"Field {self._format_attr_path(path)} ({p}) not set!")
                if default is not None:
                    self._log_thread_safe(f"Using default value instead: {default}\n")
                    return default
                self._log_thread_safe("\n")
            try:
                value = value[p]
            except:
                self._log_thread_safe(f"Error while accessing part \"{p}\" of field {self._format_attr_path(path)}:\n{traceback.format_exc()}")
                if default is not None:
                    self._log_thread_safe(f"Using default instead: {default}\n")
                    return default
                raise

        # Convert value to specified type
        try:
            value = dtype(value)
        except:
            self._log_thread_safe(f"Unable to parse value \"{value}\" from field {self._format_attr_path(path)} to {dtype}:\n{traceback.format_exc()}")
            if default is not None:
                self._log_thread_safe(f"Using default value instead: {default}\n")
                return default
            raise

        return value

    @staticmethod
    def _format_attr_path(path):
        return "->".join(path)
    
    def _convert_setting_to_data(self, path: list[str], dtype: typing.Callable[[typing.Any], T], to: list[str]|None=None, default: T|None=None) -> int:
        if to is None:
            to = path

        try:
            value = self._get_convert_setting(path, dtype, default=default)
        except Exception:
            return 1
        
        self._save_path_in_dict(self._convert_data, to, value)
        return 0
    
    def _convert_settings_to_data(self) -> int:
        errors = 0
        errors += self._convert_setting_to_data(["input", "text"], str, default="Lorem ipsum (there was an error parsing the input field)")
        errors += self._convert_setting_to_data(["output", "file"], lambda p: os.path.join(path_data, p), default="demo.gcode")

        errors += self._convert_setting_to_data(["font", "size"], float, default=10)
        errors += self._convert_setting_to_data(["font", "style"], int, default=0)
        errors += self._convert_setting_to_data(["font", "bias"], lambda x: float(x)/100, default=0.75)
        errors += self._convert_setting_to_data(["font", "lineheight"], float, default=10)

        try:
            font_size = self._convert_data.get("font", {}).get("size", 10)
            word_spacing = self._get_convert_setting(["font", "wordspacing"], float, default=font_size * 0.4)
            word_spacing_var = self._get_convert_setting(["font", "wordspacingvariance"], float, default=font_size * 0.2)
            def wordspacingfun():
                return word_spacing + (random.random()-0.5) * word_spacing_var
            self._save_path_in_dict(self._convert_data, ["font", "wordspacing"], wordspacingfun)
        except Exception:
            errors += 1

        # errors += convertSettingToData(["font", "align", "horizontal"], float, default=formatFloat(0))
        errors += self._convert_setting_to_data(["font", "align", "vertical"], float, default=0.8)

        try:
            pen_settings = {}

            mode = self._get_convert_setting(["output", "format"], str, default="gcode")
            
            # see lib/handwriting/commands.py for more information about these arguments
            pen_settings["pendraw"] = self._get_convert_setting(["pen", "heights", "draw"], float, default=0)
            pen_settings["pentravel"] = self._get_convert_setting(["pen", "heights", "travel"], float, default=5)
            pen_settings["penpause"] = self._get_convert_setting(["pen", "heights", "pause"], float, default=30)

            pen_settings["feeddraw"] = self._get_convert_setting(["pen", "speeds", "draw"], float, default=1000)
            pen_settings["feedtravel"] = self._get_convert_setting(["pen", "speeds", "travel"], float, default=1000)

            self._save_path_in_dict(self._convert_data, ["commands"], self._parse_pen_settings(mode, **pen_settings))
        except Exception:
            print(traceback.format_exc())
            errors += 1

        errors += self._convert_setting_to_data(["page", "width"], float, default=0)
        errors += self._convert_setting_to_data(["page", "height"], float, default=0)
        errors += self._convert_setting_to_data(["page", "rotate"], float, default=0)

        errors += self._convert_setting_to_data(["features", "replace", "enabled"], bool, default=True)
        errors += self._convert_setting_to_data(["features", "imitate", "enabled"], bool, default=True)
        errors += self._convert_setting_to_data(["features", "imitate", "diaresisasmacron"], bool, default=False)
        errors += self._convert_setting_to_data(["features", "splitpages", "enabled"], bool, default=False)

        return errors
    
    def _load_settings_from_file(self):
        if not os.path.isfile(path_settings):
            return
        
        file = None
        try:
            file = open(path_settings, "r")
            settings = json.load(file)
            settings = legacy.convertSettingsLegacy(settings, version_handcode)
            self._convert_settings.update(settings)
        except Exception:
            self._log_thread_safe(f"Could not load settings:\n{traceback.format_exc()}")
        finally:
            if file: file.close()

    def _save_settings_to_file(self, *, raise_on_fail: bool=False):
        self._log_thread_safe("Saving settings... ")
        try:
            file = open(path_settings, "w")
            json.dump(self._convert_settings, file)
            file.close()
        except Exception as e:
            self._log_thread_safe(f"Failed! ({e})\n")
            if raise_on_fail:
                raise
            return
        self._log_thread_safe("Done\n")

    def __init__(self):
        self._create_window()
        self._load_fonts()
        self._load_styles()
        self._init_sizes()
        self._init_state_vars()
        self._init_window()
        self._init_widgets()

    def start(self):
        self._init_handlers()

        self._prg_loading.start(20)
        threading.Thread(target=self._thread_convert, daemon=True).start()

        self._update_entire_layout()
        self.window.update()
        self._load_settings_from_file()
        
        self._schedule_ui_update()
        self.window.mainloop()

if __name__ == "__main__":
    HandCodeApp().start()
