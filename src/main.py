import prestart

import os
import re
import sys
import json
import queue
import random
import legacy
import threading
import traceback
import pkg_resources
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb


version_handcode = pkg_resources.get_distribution(projectname).version
path_exe = os.path.dirname(os.path.realpath(sys.executable if getattr(sys, "frozen", False) else __file__))
path_data = os.path.join(path_exe, "data")
path_lib = os.path.join(path_exe, "lib")
sys.path.append(path_lib) # for clean build reasons we dont include lib.handwriting
import tkwidgets as tkw

# This is just the GUI for this program, dont be intimidated.
# For the main part of the program have a look at the HandGCode class in the src/lib/handwriting/gcode.py file

versionSettingsCurrent = version_handcode
style = {
  "bg_window": "#303030",
  "bg_button": "#505050",
  "bg_button_hover": "#404040",
  "bg_button_start": "#409040",
  "bg_scroll": "#202020",
  "bg_inner": "#101010",
  "bg_separator": "#606060",
  "fg_button": "#D0D0D0",
  "fg_button_hover": "#D0D0D0",
  "fg_button_start": "#004000",
  "fg_scroll": "#808080",
  "fg_label": "#D0D0D0",
  "fg_text": "#F0F0F0",
  "fg_hint": "#A0A0A0",
  "fg_progress": "#409040",
  "relief": "flat",
  "borderwidth": 0,
  "highlightthickness": 0,
}

def main():
    window = tk.Tk()
    window.resizable(False, False)
    wsize = (660, 650)
    window.geometry(f"{wsize[0]}x{wsize[1]}")
    window.title("HandCode")
    window.configure(bg=style["bg_window"])
    if os.name == "nt":
        window.iconbitmap(os.path.join(path_lib, "icon.ico"))

    fontTooltip = tkf.Font(size=7)
    fontText = tkf.Font(size=9)
    fontLabel = tkf.Font(size=10, weight="bold")
    fontStart = tkf.Font(size=24, weight="bold")

    styleLabelSection = {
        "font": fontLabel,
        "bg": style["bg_window"],
        "fg": style["fg_label"],
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleLabelInput = {
        "font": fontText,
        "bg": style["bg_window"],
        "fg": style["fg_label"],
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleLabelTooltip = {
        "font": fontTooltip,
        "bg": style["bg_window"],
        "fg": style["fg_label"],
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleEntryDefault = {
        "bg": style["bg_inner"],
        "fg": style["fg_text"],
        "insertbackground": style["fg_hint"],
        "relief": tk.FLAT,
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    _styleEntryCustom = {
        "bgentry": style["bg_inner"],
        "fgentry": style["fg_text"],
        "bgcursor": style["fg_hint"],
        "font": fontText,
        "relief": tk.FLAT,
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleEntryScrolled = {
        **_styleEntryCustom,
        "stylescrollx": "Maddin.HC.Horizontal.TScrollbar",
        "stylescrolly": "Maddin.HC.Vertical.TScrollbar",
    }

    styleEntryUnit = {
        **_styleEntryCustom,
        "fgunit": style["fg_hint"]
    }
    
    styleEntryLabeled = {
        **styleEntryUnit,
        "bglabel": style["bg_window"],
        "fglabel": style["fg_label"],
    }

    styleButtonDefault = {
        "bg": style["bg_button"],
        "fg": style["fg_button"],
        "relief": tk.FLAT,
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleButtonStart = {
        "font": fontStart,
        "bg": style["bg_button_start"],
        "fg": style["fg_button_start"],
        "relief": tk.FLAT,
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleScaleLabeled = {
        "bglabel": style["bg_window"],
        "fglabel": style["fg_label"],
        "fgtooltip": style["fg_hint"],
        "bgscale": style["bg_inner"],
        "fgscale": style["bg_button"],
        "fgscale:hover": style["bg_button_hover"],
        "font": fontText,
        "fonttooltip": fontTooltip,
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleSelectLabeled = {
        "bglabel": style["bg_window"],
        "fglabel": style["fg_label"],
        "bgselect": style["bg_button"],
        "bgselect:hover": style["bg_button_hover"],
        "fgselect": style["fg_button"],
        "fgselect:hover": style["fg_button_hover"],
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleCheckboxDefault = {
        "bglabel": style["bg_window"],
        "bgcheck": style["bg_inner"],
        "fg": style["fg_label"],
        "font": fontText,
        "bd": style["borderwidth"],
        "highlightthickness": style["highlightthickness"],
    }

    styleCheckboxSmall = {
        **styleCheckboxDefault,
        "font": fontTooltip
    }
    
    ttkStyle = ttk.Style()
    ttkStyle.theme_use("default")
    ttkStyle.configure("Maddin.HC.Horizontal.TProgressbar", borderwidth=style["borderwidth"], troughcolor=style["bg_inner"], background=style["fg_progress"], troughrelief=style["relief"])
    ttkStyle.configure('Maddin.HC.Horizontal.TScrollbar', troughcolor=style["bg_window"], background=style["bg_button"], arrowcolor=style["fg_hint"], relief=style["relief"], troughrelief=style["relief"])
    ttkStyle.map('Maddin.HC.Horizontal.TScrollbar', background=[('pressed', '!disabled', 'active', style["bg_button_hover"])])
    ttkStyle.configure('Maddin.HC.Vertical.TScrollbar', troughcolor=style["bg_window"], background=style["bg_button"], arrowcolor=style["fg_hint"], relief=style["relief"], troughrelief=style["relief"])
    ttkStyle.map('Maddin.HC.Vertical.TScrollbar', background=[('pressed', '!disabled', 'active', style["bg_button_hover"])])


    lblFileIn = tk.Label(window, text="Input File (opt):", **styleLabelSection)
    btnFileIn = tk.Button(window, text="Open File...", **styleButtonDefault)
    lblFileProcess = tk.Label(window, text="↴   ↱", **{**styleLabelSection, "font": fontStart})
    lblFileOut = tk.Label(window, text="Output File:", **styleLabelSection)
    edtFileOut = tk.Entry(window, **styleEntryDefault)
    sltFileType = tkw.LabeledSelect(window, label="Format", options=["GCode"], **styleSelectLabeled)
    
    lblInput = tk.Label(window, text="Input Text:", **styleLabelSection)
    edtInput = tkw.ScrolledEntry(window, **styleEntryScrolled)

    lblLog = tk.Label(window, text="Event Log:", **styleLabelSection)
    edtLog = tkw.ScrolledEntry(window, **styleEntryScrolled)
    
    prgLoading = ttk.Progressbar(window, orient="horizontal", mode="indeterminate", style="Maddin.HC.Horizontal.TProgressbar")
    btnShow = tk.Button(window, text="Open input/output folder", **styleButtonDefault)
    btnStart = tk.Button(window, text="Start", **styleButtonStart, state=tk.DISABLED)
    

    segLeftRight = tk.Frame(window, bd=0, bg=style["bg_separator"])


    lblFont = tk.Label(window, text="Font Settings:", **styleLabelSection)
    edtFontSize = tkw.LabeledEntry(window, label="Size", unit="mm", **styleEntryLabeled)
    sltFontStyle = tkw.LabeledSelect(window, label="Style", options=[f"Style {i+1}" for i in range(12)], **styleSelectLabeled)
    edtFontBias = tkw.LabeledEntry(window, label="Legibility", unit="%", **styleEntryLabeled)
    
    edtFontLineHeight = tkw.LabeledEntry(window, label="Line Height", unit="mm", **styleEntryLabeled)
    lblFontWordSpacing = tk.Label(window, text="Word Spacing", **styleLabelInput)
    edtFontWordSpacing = tkw.UnitEntry(window, unit="mm", **styleEntryUnit)
    lblFontWordSpacingVar = tk.Label(window, text="±", **styleLabelInput)
    edtFontWordSpacingVar = tkw.UnitEntry(window, unit="mm", **styleEntryUnit)

    chkFontLineHeightRecalc = tkw.Checkbox(window, label="Recalc on f...", **styleCheckboxSmall)
    chkFontWordSpacingRecalc = tkw.Checkbox(window, label="Recalc on font size cha...", **styleCheckboxSmall)
    
    sclFontAlignHorizontal = tkw.LabeledScale(window, label="Horzontal Align", description="Left      Center    Right", start=0, end=1, step=0.1, **styleScaleLabeled, state=tk.DISABLED)
    sclFontAlignVertical = tkw.LabeledScale(window, label="Vertical Align", description="Top      Center  Bottom", start=0, end=1, step=0.1, **styleScaleLabeled)
    
    lblPen = tk.Label(window, text="Pen Settings:", **styleLabelSection)
    edtPenZDraw = tkw.LabeledEntry(window, label="Z Draw", unit="mm", **styleEntryLabeled)
    edtPenZTravel = tkw.LabeledEntry(window, label="Z Travel", unit="mm", **styleEntryLabeled)
    edtPenZPause = tkw.LabeledEntry(window, label="Z Pause", unit="mm", **styleEntryLabeled)

    edtPenFDraw = tkw.LabeledEntry(window, label="Feedrate Draw", unit="mm/min", **styleEntryLabeled)
    edtPenFTravel = tkw.LabeledEntry(window, label="Feedrate Travel", unit="mm/min", **styleEntryLabeled)


    lblPage = tk.Label(window, text="Page Settings:", **styleLabelSection)
    edtPageWidth = tkw.LabeledEntry(window, label="Width (o≃∞)", unit="mm", **styleEntryLabeled)
    edtPageHeight = tkw.LabeledEntry(window, label="Height (o≃∞)", unit="mm", **styleEntryLabeled)
    edtPageRotation = tkw.LabeledEntry(window, label="Rotation", unit="°", **styleEntryLabeled)
    
    lblOther = tk.Label(window, text="Other Features:", **styleLabelSection)
    chkFeatureReplace = tkw.Checkbox(window, label="Replace unknown characters", **styleCheckboxDefault)
    lblFeatureReplace = tk.Label(window, text="(e.g. ä -> a, Q -> O)", **styleLabelTooltip)
    chkFeatureImitate = tkw.Checkbox(window, label="Imitate some unknown characters", **styleCheckboxDefault)
    chkFeatureImitateDAM = tkw.Checkbox(window, label="Imitate diaresis as macron (ä -> ā)", **styleCheckboxSmall)
    chkFeatureSplitPages = tkw.Checkbox(window, label="One output file for each page", **styleCheckboxDefault)

    def reloadUI():
        # set listeners

        _fontfactors = dict()
        def recalculateFontSize(base, entry, name, digits=-1):
            if name not in _fontfactors:
                return
            template = "{size}"
            if digits > 0:
                template = f"{{size:.0{digits}f}}"
            size = base * _fontfactors[name]
            entry.set(template.format(size=size).rstrip("0").rstrip("."))

        def getFontSize(entry):
            size = -1
            try:
                size = float(entry.get().strip())
            except:
                pass # bad, i know...

            return size
            
        def recalculateFontSizes():
            _fontSize = getFontSize(edtFontSize)
            if _fontSize < 0:
                return

            if chkFontLineHeightRecalc.get():
                recalculateFontSize(_fontSize, edtFontLineHeight, "lineheight", digits=4)
            if chkFontWordSpacingRecalc.get():
                recalculateFontSize(_fontSize, edtFontWordSpacing, "wordspacing", digits=2)
                recalculateFontSize(_fontSize, edtFontWordSpacingVar, "wordspacingvar", digits=1)

        def recalculateFontFactor(base, entry, name):
            size = getFontSize(entry)
            _fontfactors[name] = size/base
        def recalculateFontFactors():
            _fontSize = getFontSize(edtFontSize)
            if _fontSize <= 0:
                return
            
            if chkFontLineHeightRecalc.get():
                recalculateFontFactor(_fontSize, edtFontLineHeight, "lineheight")
            else:
                _fontfactors.pop("lineheight", None)
            if chkFontWordSpacingRecalc.get():
                recalculateFontFactor(_fontSize, edtFontWordSpacing, "wordspacing")
                recalculateFontFactor(_fontSize, edtFontWordSpacingVar, "wordspacingvar")
            else:
                _fontfactors.pop("wordspacing", None)
                _fontfactors.pop("wordspacingvar", None)
        
        edtFontSize.addListener("change", recalculateFontSizes)
        edtFontLineHeight.addListener("change", recalculateFontFactors)
        edtFontWordSpacing.addListener("change", recalculateFontFactors)
        edtFontWordSpacingVar.addListener("change", recalculateFontFactors)
        chkFontLineHeightRecalc.addListener("change", recalculateFontFactors)
        chkFontWordSpacingRecalc.addListener("change", recalculateFontFactors)
        

        def updateFeatureImitate():
            state = tk.NORMAL if chkFeatureImitate.get() else tk.DISABLED
            chkFeatureImitateDAM.configure(state=state)
        chkFeatureImitate.addListener("change", updateFeatureImitate)

        def showFolder():
            if os.name == "nt":
                os.startfile(path_data)
            elif sys.platform.startswith("linux"):
                os.system(f"xdg-open \"{path_data}\"") # TODO: dangerous, we assume the path does not contain any quotes
        btnShow.configure(command=showFolder)
        btnStart.configure(command=startConvert)

        
        # actually display all the ui stuff

        xstart = 10; ystart = 5
        xmargin = 10; ymargin = 5
        height = 20
        x = xstart; y = ystart
        
        lblFileIn.place(x=x, y=y, height=height)
        btnFileIn.place(x=x, y=y+height, width=120, height=height)
        btnFileIn.configure(command=selectInputFile)
        lblFileProcess.place(x=x+120, y=y+height-2)
        lblFileOut.place(x=x+120+70, y=y, height=height)
        edtFileOut.place(x=x+120+70, y=y+height, width=120, height=height)
        sltFileType.place(x=x+120+70+120+xmargin, y=y, width=80)

        y += height + height + ymargin
        lblInput.place(x=x, y=y, height=height)
        y += height
        edtInput.place(x=x, y=y, width=400, height=430)

        y += 430 + ymargin
        lblLog.place(x=x, y=y, height=height)
        y += height
        edtLog.place(x=x, y=y, width=400, height=114)
        
        x += 400 + xmargin; y = ystart
        segLeftRight.place(x=x-1, y=y+ymargin, width=2, height=wsize[1]-2*(ystart+ymargin))
        
        x += xmargin
        lblFont.place(x=x, y=y, height=20)
        y += height
        edtFontSize.place(x=x, y=y, width=60)
        sltFontStyle.place(x=x+60+xmargin, y=y, width=80)
        edtFontBias.place(x=x+60+xmargin+80+xmargin, y=y, width=60)

        y += 2 * height + ymargin
        edtFontLineHeight.place(x=x, y=y, width=80)
        lblFontWordSpacing.place(x=x+80+xmargin, y=y, width=100, height=height)
        edtFontWordSpacing.place(x=x+80+xmargin, y=y+height, width=65)
        lblFontWordSpacingVar.place(x=x+80+xmargin+65, y=y+height, width=15, height=height)
        edtFontWordSpacingVar.place(x=x+80+xmargin+65+15, y=y+height, width=50)
        y += 2 * height
        chkFontLineHeightRecalc.place(x=x-3, y=y, height=height)
        chkFontWordSpacingRecalc.place(x=x+80+xmargin-3, y=y, height=height)

        y += height + ymargin
        sclFontAlignHorizontal.place(x=x, y=y, width=105)
        sclFontAlignVertical.place(x=x+105+xmargin, y=y, width=105)

        y += 2 * height + 10 + 3 * ymargin  # + 10 since the LabeledScale is 10px larger than 2 * height
        lblPen.place(x=x, y=y, height=height)
        y += height
        edtPenZDraw.place(x=x, y=y, width=67)
        edtPenZTravel.place(x=x+67+xmargin, y=y, width=66)
        edtPenZPause.place(x=x+67+xmargin+66+xmargin, y=y, width=67)

        y += 2 * height + ymargin
        edtPenFDraw.place(x=x, y=y, width=105)
        edtPenFTravel.place(x=x+105+xmargin, y=y, width=105)

        y += 2 * height + 3 * ymargin
        lblPage.place(x=x, y=y, height=height)
        y += height
        edtPageWidth.place(x=x, y=y, width=75)
        edtPageHeight.place(x=x+75+xmargin, y=y, width=75)
        edtPageRotation.place(x=x+75+xmargin+75+xmargin, y=y, width=50)

        y += 2 * height + 3 * ymargin
        lblOther.place(x=x, y=y, height=height)
        y += height
        chkFeatureReplace.place(x=x, y=y, height=height)
        y += height
        lblFeatureReplace.place(x=x+height, y=y, height=height//2)
        y += height//2 + ymargin
        chkFeatureImitate.place(x=x, y=y, height=height)
        y += height
        chkFeatureImitateDAM.place(x=x+height, y=y, height=height-5)
        y += height + ymargin
        chkFeatureSplitPages.place(x=x, y=y, height=height)

        y += height + 3 * ymargin - 2
        prgLoading.place(x=x, y=y, width=220, height=height)
        y += height + ymargin + 2
        btnShow.place(x=x, y=y, width=220, height=height+ymargin)
        y += height + ymargin + 2 * ymargin
        btnStart.place(x=x, y=y, width=220, height=2*height+2*ymargin)

    uiQueue = queue.Queue()
    uiPollInterval = 100
    def updateUIQueue():
        try:
            cb = uiQueue.get(0)
            cb()
        except queue.Empty:
            pass
        except Exception as e:
            tkmb.showerror("Error in the UI polling loop", f"The following unhandled exception occured: {e}\n\n{traceback.format_exc()}\n\n{sys.exc_info()}")

        window.after(uiPollInterval, updateUIQueue)

    def startConvert():
        if convertEvent.is_set():
            return
        btnStart.configure(state=tk.DISABLED)
        edtLog.set("")
        prgLoading.start()
        readSettingsFromUI()
        saveSettingsToFile()
        errors = convertSettingsToData()
        if errors:
            report("log", f"\n{errors} errors were encountered while parsing your current settings. Please see above for more information.\n")
            prgLoading.stop()
            return
        convertEvent.set()

    def threadConvert():
        try:
            reportThreadSafe("log", "Loading tensorflow... ")
            import handwriting
            reportThreadSafe("log", "Done\nLoading neural network... ")
            gcode = handwriting.gcode.HandGCode(logger=lambda s: reportThreadSafe("log", s))
            reportThreadSafe("log", "Done\nLoading helper functions... ")
            _pensettingsgen["gcode"] = handwriting.commands.gcode
            reportThreadSafe("log", "Done\n")
            reportThreadSafe("success")
            while True:
                convertEvent.wait()
                try:
                    gcode.generate(convertData)
                    report("success")
                except Exception as e:
                    reportThreadSafe("error", e)
                convertEvent.clear()
        except Exception as e:
            tkmb.showerror("Error in the neural network thread", f"The following unhandled exception occured: {e}\n\n{traceback.format_exc()}\n\n{sys.exc_info()}")

    def reportThreadSafe(event, data=None):
        uiQueue.put(lambda: report(event, data=data))

    def report(event, data=None):
        if (event == "log") and data:
            edtLog.append(data)

        if (event == "success"):
            btnStart.configure(state=tk.NORMAL)
            prgLoading.stop()
            
        if (event == "error"):
            btnStart.configure(state=tk.NORMAL)
            prgLoading.stop()
            report("log", f"\nUnhandled error: {data}\n")
            print(f"An error occurred:\n{traceback.format_exc()}\n\n{sys.exc_info()}")

    def selectInputFile():
        filename = tkfd.askopenfilename(title="Open text file...", initialdir="data")
        if not filename:
            report("log", "No file selected!\n")
            return
        readInputFile(filename)

    def readInputFile(filename):
        if not filename:
            return
        file = None
        try:
            file = open(filename, "r")
            edtInput.set(file.read())
        except Exception as e:
            report("log", f"Unknown error reading file: {e}")
        finally:
            if file:
                file.close()

    def _savePathInDict(d, path, value):
        plen = len(path)
        for i, p in enumerate(path, 1):
            if i < plen:
                if p not in d:
                    d[p] = dict()
                d = d[p]
                continue
            d[p] = value

    def saveSetting(path, value):
        _savePathInDict(convertSettings, path, value)

    def readSettingsFromUI():
        convertSettings.clear()
        convertSettings["version"] = versionSettingsCurrent
        saveSetting(["input", "text"], edtInput.get())
        saveSetting(["output", "file"], edtFileOut.get())
        saveSetting(["output", "format"], sltFileType.get())

        saveSetting(["font", "size"], edtFontSize.get())
        saveSetting(["font", "style"], sltFontStyle.get())
        saveSetting(["font", "bias"], edtFontBias.get())
        saveSetting(["font", "lineheight"], edtFontLineHeight.get())
        saveSetting(["font", "wordspacing"], edtFontWordSpacing.get())
        saveSetting(["font", "wordspacingvariance"], edtFontWordSpacingVar.get())
        #saveSetting(["font", "align", "horizontal"], sclFontAlignHorizontal.get())
        saveSetting(["font", "align", "vertical"], sclFontAlignVertical.get())

        saveSetting(["pen", "heights", "draw"], edtPenZDraw.get())
        saveSetting(["pen", "heights", "travel"], edtPenZTravel.get())
        saveSetting(["pen", "heights", "pause"], edtPenZPause.get())
        saveSetting(["pen", "speeds", "draw"], edtPenFDraw.get())
        saveSetting(["pen", "speeds", "travel"], edtPenFTravel.get())

        saveSetting(["page", "width"], edtPageWidth.get())
        saveSetting(["page", "height"], edtPageHeight.get())
        saveSetting(["page", "rotate"], edtPageRotation.get())

        saveSetting(["features", "replace", "enabled"], chkFeatureReplace.get())
        saveSetting(["features", "imitate", "enabled"], chkFeatureImitate.get())
        saveSetting(["features", "imitate", "diaresisasmacron"], chkFeatureImitateDAM.get())
        saveSetting(["features", "splitpages", "enabled"], chkFeatureSplitPages.get())
        
    formatFloat = legacy.formatFloat
    formatFontStyleName = legacy.formatFontStyleName
    
    def writeSettingsToUI():
        edtInput.set(convertSettings.get("input", {}).get("text", ""))
        edtFileOut.delete(0, tk.END)
        edtFileOut.insert(0, convertSettings.get("output", {}).get("file", "demo.nc"))
        sltFileType.set(convertSettings.get("output", {}).get("format", "GCode"))

        settingsFont = convertSettings.get("font", {})
        fontSize = settingsFont.get("size", formatFloat(10))
        _fontSize = 10
        try: _fontSize = float(fontSize)
        except: pass
        edtFontSize.set(fontSize)
        sltFontStyle.set(settingsFont.get("style", formatFontStyleName(1)))
        edtFontBias.set(settingsFont.get("bias", formatFloat(75)))
        edtFontLineHeight.set(settingsFont.get("lineheight", fontSize))
        edtFontWordSpacing.set(settingsFont.get("wordspacing", formatFloat(round(_fontSize * 0.4, 2))))
        edtFontWordSpacingVar.set(settingsFont.get("wordspacingvariance", formatFloat(round(_fontSize * 0.2, 1))))
        chkFontLineHeightRecalc.set(settingsFont.get("lineheight_recalc", True))
        chkFontWordSpacingRecalc.set(settingsFont.get("wordspacing_recalc", True))
        chkFontWordSpacingRecalc.callListeners("change")

        settingsFontAlign = settingsFont.get("align", {})
        sclFontAlignHorizontal.set(settingsFontAlign.get("horizontal", 0))
        sclFontAlignVertical.set(settingsFontAlign.get("vertical", 0.8))

        settingsPen = convertSettings.get("pen", {})
        settingsPenHeights = settingsPen.get("heights", {})
        edtPenZDraw.set(settingsPenHeights.get("draw", formatFloat(0)))
        edtPenZTravel.set(settingsPenHeights.get("travel", formatFloat(5)))
        edtPenZPause.set(settingsPenHeights.get("pause", formatFloat(30)))
        settingsPenSpeeds = settingsPen.get("speeds", {})
        edtPenFDraw.set(settingsPenSpeeds.get("draw", formatFloat(1000)))
        edtPenFTravel.set(settingsPenSpeeds.get("draw", formatFloat(1000)))

        settingsPage = convertSettings.get("page", {})
        edtPageWidth.set(settingsPage.get("width", formatFloat(0)))
        edtPageHeight.set(settingsPage.get("height", formatFloat(0)))
        edtPageRotation.set(settingsPage.get("rotate", formatFloat(0)))

        settingsFeatures = convertSettings.get("features", {})
        chkFeatureReplace.set(settingsFeatures.get("replace", {}).get("enabled", True))
        chkFeatureImitate.set(settingsFeatures.get("imitate", {}).get("enabled", True))
        chkFeatureImitate.callListeners("change")
        chkFeatureImitateDAM.set(settingsFeatures.get("imitate", {}).get("diaresisasmacron", False))
        chkFeatureSplitPages.set(settingsFeatures.get("splitpages", {}).get("enabled", False))


    def formatPath(path):
        return "->".join(path)

    _fontstylere = re.compile("^\s*Style (\d+)\s*$")
    def parseFontStyle(style):
        style = _fontstylere.findall(style)
        try:
            style = int(style[0])
            if (style < 1) or (style > 12):
                raise ValueError()
            return style
        except (KeyError, ValueError):
            report("log", f"Invalid font style selected: \"{style}\"\n")
            raise
        except Exception as e:
            report("log", f"Unknown error while parsing font style \"{style}\": {e}\n")
            raise

    _pensettingsgen = dict()
    def parsePenSettings(mode, **kwargs):
        if not _pensettingsgen:
            raise NotImplemented("The handwriting library does not seem to have been fully loaded yet!")
        if mode not in _pensettingsgen:
            raise NotImplemented("The mode you requested does not seem to be implemented (yet?).")

        return _pensettingsgen[mode](**kwargs)
        
    def getConvertSetting(path, default=None):
        value = convertSettings
        for p in path:
            if p not in value:
                report("log", f"Field {formatPath(path)} ({p}) not set!")
                if default is not None:
                    report("log", f" Using default value instead: {default}\n")
                    return default
                report("log", "\n")
                raise
            try:
                value = value[p]
            except Exception as e:
                report("log", f"Error while accessing part \"{p}\" of field {formatPath(path)}:\n{traceback.format_exc()}")
                if default is not None:
                    report("log", f"Using default value instead: {default}\n")
                    return default
                raise
        return value

    def getConvertSettingTyped(path, dtype, default=None):
        value = getConvertSetting(path, default=default)
        try:
            value = dtype(value)
        except Exception as e:
            report("log", f"Unable to parse value \"{value}\" from field {formatPath(path)} to {dtype}:\n{traceback.format_exc()}")
            try:
                value = dtype(default)
                report("log", f"Using default value instead: {default} -> {value}\n")
                return value
            except:
                pass
            raise
        
        return value

    def convertSettingToData(path, dtype, to=None, default=None):
        if to is None:
            to = path

        try:
            value = getConvertSettingTyped(path, dtype, default=default)
        except:
            return 1
        
        _savePathInDict(convertData, to, value)
        return 0

    def convertSettingsToData():
        errors = 0
        errors += convertSettingToData(["input", "text"], str, default="Lorem ipsum (there was an error parsing the input field)")
        errors += convertSettingToData(["output", "file"], lambda p: os.path.join("data", p), default="demo.gcode")

        errors += convertSettingToData(["font", "size"], float, default=formatFloat(10))
        errors += convertSettingToData(["font", "style"], parseFontStyle, default=formatFontStyleName(1))
        errors += convertSettingToData(["font", "bias"], lambda x: float(x)/100, default=formatFloat(75))
        errors += convertSettingToData(["font", "lineheight"], float, default=formatFloat(10))

        try:
            _fontSize = convertData.get("font", {}).get("size", 10)
            wordspacing = getConvertSettingTyped(["font", "wordspacing"], float, default=formatFloat(_fontSize * 0.4))
            wordspacingvar = getConvertSettingTyped(["font", "wordspacingvariance"], float, default=formatFloat(_fontSize * 0.2))
            def wordspacingfun():
                return wordspacing + (random.random()-0.5) * wordspacingvar
            _savePathInDict(convertData, ["font", "wordspacing"], wordspacingfun)
        except:
            errors += 1

        # errors += convertSettingToData(["font", "align", "horizontal"], float, default=formatFloat(0))
        errors += convertSettingToData(["font", "align", "vertical"], float, default=formatFloat(0.8))

        try:
            pensettings = dict()

            mode = getConvertSettingTyped(["output", "format"], str, default="GCode").lower()

            # see lib/handwriting/commands.py for more information about these arguments
            pensettings["pendraw"] = getConvertSettingTyped(["pen", "heights", "draw"], float, default=formatFloat(0))
            pensettings["pentravel"] = getConvertSettingTyped(["pen", "heights", "travel"], float, default=formatFloat(5))
            pensettings["penpause"] = getConvertSettingTyped(["pen", "heights", "pause"], float, default=formatFloat(30))
            
            pensettings["feeddraw"] = getConvertSettingTyped(["pen", "speeds", "draw"], float, default=formatFloat(1000))
            pensettings["feedtravel"] = getConvertSettingTyped(["pen", "speeds", "travel"], float, default=formatFloat(1000))

            _savePathInDict(convertData, ["commands"], parsePenSettings(mode, **pensettings))
        except:
            print(traceback.format_exc())
            errors += 1

        errors += convertSettingToData(["page", "width"], float, default=formatFloat(0))
        errors += convertSettingToData(["page", "height"], float, default=formatFloat(0))
        errors += convertSettingToData(["page", "rotate"], float, default=formatFloat(0))

        errors += convertSettingToData(["features", "replace", "enabled"], bool, default=True)
        errors += convertSettingToData(["features", "imitate", "enabled"], bool, default=True)
        errors += convertSettingToData(["features", "imitate", "diaresisasmacron"], bool, default=False)
        errors += convertSettingToData(["features", "splitpages", "enabled"], bool, default=False)

        return errors

    _pathSettings = os.path.join("data", "settings.json")
    def loadSettingsFromFile():
        if not os.path.isfile(_pathSettings):
            return
        
        file = None
        try:
            file = open(_pathSettings, "r")
            settings = json.load(file)
            settings = legacy.convertSettingsLegacy(settings, versionSettingsCurrent)
            convertSettings.update(settings)
        except Exception as e:
            print("Could not load settings: ")
            print(traceback.format_exc())
        finally:
            if file: file.close()

    def saveSettingsToFile():
        report("log", "Saving settings... ")
        file = open(_pathSettings, "w")
        json.dump(convertSettings, file)
        file.close()
        report("log", "Done\n")

    prgLoading.start(20)
    convertEvent = threading.Event()
    convertData = dict()
    convertSettings = dict()
    convertThread = threading.Thread(target=threadConvert, daemon=True)
    convertThread.start()

    reloadUI()
    window.update()
    loadSettingsFromFile()
    writeSettingsToUI()

    window.after(2*uiPollInterval, updateUIQueue)
    window.mainloop()

if __name__ == "__main__":
    main()
