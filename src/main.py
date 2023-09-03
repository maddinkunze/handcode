import prestart

import os
import sys
import json
import threading
import traceback
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb

# This is just the GUI for this program, dont be intimidated.
# For the main part of the program have a look at the convert() function in the convert.py file

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
  "borderwidth": 0
}

def main():
    window = tk.Tk()
    window.resizable(False, False)
    window.geometry("220x60")
    window.title("HandCode")
    window.configure(bg=style["bg_window"])
    window.iconbitmap(os.path.join("lib", "icon.ico"))

    ttkStyle = ttk.Style()
    ttkStyle.theme_use("default")
    ttkStyle.configure("Maddin.HC.Horizontal.TProgressbar", borderwidth=style["borderwidth"], troughcolor=style["bg_inner"], background=style["fg_progress"], troughrelief=style["relief"])
    ttkStyle.configure('Maddin.HC.Horizontal.TScrollbar', troughcolor=style["bg_window"], background=style["bg_button"], arrowcolor=style["fg_hint"], relief=style["relief"], troughrelief=style["relief"])
    ttkStyle.map('Maddin.HC.Horizontal.TScrollbar', background=[('pressed', '!disabled', 'active', style["bg_button_hover"])])
    ttkStyle.configure('Maddin.HC.Vertical.TScrollbar', troughcolor=style["bg_window"], background=style["bg_button"], arrowcolor=style["fg_hint"], relief=style["relief"], troughrelief=style["relief"])
    ttkStyle.map('Maddin.HC.Vertical.TScrollbar', background=[('pressed', '!disabled', 'active', style["bg_button_hover"])])

    fontText = tkf.Font(size=9)
    fontLabel = tkf.Font(size=10, weight="bold")
    fontStart = tkf.Font(size=24, weight="bold")

    lblLoading = tk.Label(window, text="Loading neural network...")
    lblLoading.configure(bg=style["bg_window"], fg=style["fg_hint"])
    lblLoading.place(x=10, y=5)
    prgLoading = ttk.Progressbar(window, orient="horizontal", mode="indeterminate")
    prgLoading.configure(style="Maddin.HC.Horizontal.TProgressbar")
    prgLoading.place(x=10, y=30, width=200, height=20)
    prgLoading.start(20)

    lblFilename = tk.Label(window, text="Filename:")
    lblFilename.configure(font=fontLabel, bg=style["bg_window"], fg=style["fg_label"])
    edtFilename = tk.Entry(window)
    edtFilename.configure(font=fontText, insertbackground=style["fg_hint"], bg=style["bg_inner"], fg=style["fg_text"], relief=style["relief"])
    btnFileselect = tk.Button(window, text="...")
    btnFileselect.configure(bg=style["bg_button"], fg=style["fg_button"], relief=style["relief"])
    btnFilereload = tk.Button(window, text="⟳")
    btnFilereload.configure(bg=style["bg_button"], fg=style["fg_button"], relief=style["relief"])
    lblFileext = tk.Label(window, text="Export extension:")
    lblFileext.configure(font=fontLabel, bg=style["bg_window"], fg=style["fg_label"])
    edtFileext = tk.Entry(window)
    edtFileext.configure(font=fontText, insertbackground=style["fg_hint"], bg=style["bg_inner"], fg=style["fg_text"], relief=style["relief"])
    lblInput = tk.Label(window, text="Input text:")
    lblInput.configure(font=fontLabel, bg=style["bg_window"], fg=style["fg_label"])
    edtInput = tk.Text(window, wrap="none")
    edtInput.configure(font=fontText, insertbackground=style["fg_hint"], bg=style["bg_inner"], fg=style["fg_text"], relief=style["relief"])
    scrInputX = ttk.Scrollbar(window, orient="horizontal", command=edtInput.xview)
    scrInputX.configure(style="Maddin.HC.Horizontal.TScrollbar")
    scrInputY = ttk.Scrollbar(window, orient="vertical", command=edtInput.yview)
    scrInputY.configure(style="Maddin.HC.Vertical.TScrollbar")
    edtInput.configure(xscrollcommand=scrInputX.set, yscrollcommand=scrInputY.set)

    segLeftRight = tk.Frame(window, bd=0, bg=style["bg_separator"])

    lblFont = tk.Label(window, text="Font Settings:")
    lblFont.configure(font=fontLabel, bg=style["bg_window"], fg=style["fg_label"])
    lblFontsize = tk.Label(window, text="Size")
    lblFontsize.configure(font=fontText, bg=style["bg_window"], fg=style["fg_label"])
    edtFontsize = tk.Entry(window)
    edtFontsize.configure(font=fontText, insertbackground=style["fg_hint"], bg=style["bg_inner"], fg=style["fg_text"], relief=style["relief"])
    lblFontstyle = tk.Label(window, text="Style")
    lblFontstyle.configure(font=fontText, bg=style["bg_window"], fg=style["fg_label"])
    varFontstyle = tk.StringVar()
    sltFontstyle = tk.OptionMenu(window, varFontstyle, *[f"Style {i+1}" for i in range(12)])
    sltFontstyle.configure(font=fontText, highlightthickness=0, relief=style["relief"], borderwidth=style["borderwidth"], bg=style["bg_button"], fg=style["fg_button"], activebackground=style["bg_button_hover"], activeforeground=style["fg_button_hover"])
    sltFontstyle["menu"].configure(font=fontText, relief=style["relief"], bg=style["bg_button"], fg=style["fg_button"], activebackground=style["bg_button_hover"], activeforeground=style["fg_button_hover"])
    lblFontbias = tk.Label(window, text="Legibility")
    lblFontbias.configure(font=fontText, bg=style["bg_window"], fg=style["fg_label"])
    edtFontbias = tk.Entry(window)
    edtFontbias.configure(font=fontText, insertbackground=style["fg_hint"], bg=style["bg_inner"], fg=style["fg_text"], relief=style["relief"])
    
    lblPen = tk.Label(window, text="Pen Settings:")
    lblPen.configure(font=fontLabel, bg=style["bg_window"], fg=style["fg_label"])
    lblPenup = tk.Label(window, text="Z Up/Travel")
    lblPenup.configure(font=fontText, bg=style["bg_window"], fg=style["fg_label"])
    edtPenup = tk.Entry(window)
    edtPenup.configure(font=fontText, insertbackground=style["fg_hint"], bg=style["bg_inner"], fg=style["fg_text"], relief=style["relief"])
    lblPendown = tk.Label(window, text="Z Down/Writing")
    lblPendown.configure(font=fontText, bg=style["bg_window"], fg=style["fg_label"])
    edtPendown = tk.Entry(window)
    edtPendown.configure(font=fontText, insertbackground=style["fg_hint"], bg=style["bg_inner"], fg=style["fg_text"], relief=style["relief"])
    
    lblOther = tk.Label(window, text="Other Settings:")
    lblOther.configure(font=fontLabel, bg=style["bg_window"], fg=style["fg_label"])
    varSwapXY = tk.IntVar(window)
    lblSwapXY = tk.Label(window, text="Swap X/Y Axis (Rotate 90°)")
    lblSwapXY.configure(font=fontText, bg=style["bg_window"], fg=style["fg_label"])
    chkSwapXY = tk.Checkbutton(window, variable=varSwapXY, onvalue=1, offvalue=0)
    chkSwapXY.configure(relief=style["relief"], highlightthickness=0, bg=style["bg_window"], activebackground=style["bg_window"], fg=style["fg_text"], selectcolor=style["bg_inner"], bd=style["borderwidth"])

    lblLog = tk.Label(window, text="Event Log:")
    lblLog.configure(font=fontLabel, bg=style["bg_window"], fg=style["fg_label"])
    edtLog = tk.Text(window, wrap="none")
    edtLog.configure(font=fontText, insertbackground=style["fg_hint"], bg=style["bg_inner"], fg=style["fg_text"], relief=style["relief"])
    scrLogX = ttk.Scrollbar(window, orient="horizontal", command=edtLog.xview)
    scrLogX.configure(style="Maddin.HC.Horizontal.TScrollbar")
    scrLogY = ttk.Scrollbar(window, orient="vertical", command=edtLog.yview)
    scrLogY.configure(style="Maddin.HC.Vertical.TScrollbar")
    edtLog.configure(xscrollcommand=scrLogX.set, yscrollcommand=scrLogY.set)
    btnShow = tk.Button(window, text="Open input/output folder")
    btnShow.configure(bg=style["bg_button"], fg=style["fg_button"], relief=style["relief"])
    btnStart = tk.Button(window, text="Start")
    btnStart.configure(font=fontStart, bg=style["bg_button_start"], fg=style["fg_button_start"], relief=style["relief"])
    

    def startConvert():
        if convertEvent.isSet():
            return
        if loadedCounter["current"] < loadedCounter["required"]:
            return
        btnStart.configure(state=tk.DISABLED)
        edtLog.delete(1.0, tk.END)
        prgLoading.start()
        getConvertData()
        saveSettings()
        convertEvent.set()

    def threadConvert():
        try:
            import convert
            report("loaded")
            log = lambda s: report("log", s)
            while True:
                convertEvent.wait()
                try:
                    convert.convert(**convertData, log=log)
                    report("success")
                except Exception as e:
                    report("error", e)
                convertEvent.clear()
        except Exception as e:
            tkmb.showerror("Error in the neural network thread", f"The following unhandled exception occured: {e}\n\n{traceback.format_exc()}\n\n{sys.exc_info()}")
            

    def loadUI():
        lblLoading.place_forget()
        window.geometry("660x505")

        lblFilename.place(x=10, y=5, height=20)
        edtFilename.place(x=10, y=25, width=150, height=20)
        btnFileselect.place(x=165, y=25, width=20, height=20)
        btnFileselect.configure(command=selectInputFile)
        btnFilereload.place(x=190, y=25, width=20, height=20)
        btnFilereload.configure(command=reloadInputFile)
        lblFileext.place(x=220, y=5, height=20)
        edtFileext.place(x=220, y=25, width=100, height=20)
        lblInput.place(x=10, y=50, height=20)
        edtInput.place(x=10, y=70, width=385, height=410)
        scrInputX.place(x=10, y=480, width=385, height=15)
        scrInputY.place(x=395, y=70, width=15, height=410)

        segLeftRight.place(x=419, y=10, width=2, height=485)

        lblFont.place(x=430, y=5, height=20)
        lblFontsize.place(x=430, y=25, width=60, height=20)
        edtFontsize.place(x=430, y=45, width=60, height=20)
        lblFontstyle.place(x=500, y=25, width=80, height=20)
        sltFontstyle.place(x=500, y=45, width=80, height=20)
        lblFontbias.place(x=590, y=25, width=60, height=20)
        edtFontbias.place(x=590, y=45, width=60, height=20)

        lblPen.place(x=430, y=80, height=20)
        lblPenup.place(x=430, y=100, width=105, height=20)
        edtPenup.place(x=430, y=120, width=105, height=20)
        lblPendown.place(x=545, y=100, width=105, height=20)
        edtPendown.place(x=545, y=120, width=105, height=20)

        lblOther.place(x=430, y=150, height=20)
        lblSwapXY.place(x=430, y=170, height=20)
        chkSwapXY.place(x=630, y=170, width=20, height=20)

        lblLog.place(x=430, y=200, height=20)
        edtLog.place(x=430, y=220, width=205, height=125)
        scrLogX.place(x=430, y=345, width=205, height=15)
        scrLogY.place(x=635, y=220, width=15, height=125)
        prgLoading.place(x=430, y=380, width=220, height=20)
        btnShow.place(x=430, y=410, width=220, height=25)
        btnStart.place(x=430, y=445, width=220, height=50)
        btnStart.configure(command=startConvert)

        prgLoading.stop()
        

    loadedCounter = {"current": 0, "required": 2}
    def report(event, data=None):
        if (event == "loaded"):
            loadedCounter["current"] += 1
            if loadedCounter["current"] < loadedCounter["required"]:
                return
            loadUI()
            return

        if (event == "log") and data:
            edtLog.insert(tk.END, data)

        if (event == "success"):
            btnStart.configure(state=tk.NORMAL)
            prgLoading.stop()
        if (event == "error"):
            btnStart.configure(state=tk.NORMAL)
            prgLoading.stop()
            report("log", f"Unhandled error: {data}\n")

    def selectInputFile():
        filename = tkfd.askopenfilename(title="Open text file...", initialdir="data")
        if not filename:
            report("log", "No file selected!\n")
            return

        if os.path.samefile(os.path.dirname(filename), "data"):
            filename = os.path.split(filename)[1]
        edtFilename.delete(0, tk.END)
        edtFilename.insert(0, filename)
        reloadInputFile()

    def reloadInputFile():
        _filepath = os.path.join("data", edtFilename.get())
        if not os.path.isfile(_filepath):
            report("log", "File does not exist!\n")
            return

        file = None
        try:
            file = open(_filepath, "r")
            edtInput.delete(1.0, tk.END)
            edtInput.insert(1.0, file.read())
        except Exception as e:
            report("log", f"Unknown error reading file: {e}")
        finally:
            if file: file.close()
        

    def _getConvertDataFloat(name, entry):
        value = "None/Error"
        try:
            value = entry.get()
            convertData[name] = float(value)
            return 0
        except ValueError:
            report("log", f"Invalid value \"{value}\" in field \"{name}\". It should be a (floating point) number.\n")
            return 1
        except Exception as e:
            report("log", f"Unknown error in field {entry}: {e}\n")

    def getConvertData():
        invalidData = 0
        
        convertData["filename"] = edtFilename.get()
        if not convertData["filename"]:
            convertData["filename"] = "demo.txt"
            report("log", f"Empty filename, falling back to \"demo.txt\".\n")
            invalidData += 1

        _fileverb = "Creating"
        _filepath = os.path.join("data", os.path.split(convertData["filename"])[1])
        if os.path.isfile(_filepath):
            _fileverb = "Updating"

        report("log", f"{_fileverb} file \"{_filepath}\"... ")
        filename = os.path.join("data", convertData["filename"])
        _content = edtInput.get(1.0, tk.END)
        if _content.endswith("\n"):
            _content = _content[:-1]
        file = open(filename, "w")
        file.write(_content)
        file.close()
        report("log", "Done\n")
            
        convertData["saveext"] = edtFileext.get()
        invalidData += _getConvertDataFloat("penup", edtPenup)
        invalidData += _getConvertDataFloat("pendown", edtPendown)
        invalidData += _getConvertDataFloat("fontsize", edtFontsize)
        invalidData += _getConvertDataFloat("fontbias", edtFontbias)
        try:
            convertData["fontstyle"] = int(varFontstyle.get()[6:])
        except Exception as e:
            report("log", f"Unknown error in field fontstyle: {e}\n")
            invalidData += 1
        convertData["swapXY"] = varSwapXY.get()
        verifyConvertData()

    def setConvertData():
        verifyConvertData()
        edtFilename.delete(0, tk.END)
        edtFilename.insert(0, convertData["filename"])

        edtFileext.delete(0, tk.END)
        edtFileext.insert(0, convertData["saveext"])

        edtFontsize.delete(0, tk.END)
        edtFontsize.insert(0, convertData["fontsize"])
        varFontstyle.set(f"Style {convertData['fontstyle']}")
        edtFontbias.delete(0, tk.END)
        edtFontbias.insert(0, convertData["fontbias"])

        edtPenup.delete(0, tk.END)
        edtPenup.insert(0, convertData["penup"])
        edtPendown.delete(0, tk.END)
        edtPendown.insert(0, convertData["pendown"])

        varSwapXY.set(convertData["swapXY"])

    def verifyConvertData():
        if "filename" not in convertData:
            print(convertData)
            convertData["filename"] = "demo.txt"
        _filepath = os.path.join("data", convertData["filename"])
        _datapath = os.path.abspath("data")
        if (not os.path.isfile(_filepath)) and (not os.path.samefile(os.path.commonpath([os.path.abspath(_filepath), _datapath]), _datapath)):
            convertData["filename"] = "demo.txt"
            print("replace 2")

        if "saveext" not in convertData:
            convertData["saveext"] = "gcode"

        if "pendown" not in convertData:
            convertData["pendown"] = 0
        if "penup" not in convertData:
            convertData["penup"] = 5

        if "fontsize" not in convertData:
            convertData["fontsize"] = 10
        if "fontstyle" not in convertData:
            convertData["fontstyle"] = 1
        if "fontbias" not in convertData:
            convertData["fontbias"] = 0.75

        if "swapXY" not in convertData:
            convertData["swapXY"] = False
        if "linespernewline" not in convertData:
            convertData["linespernewline"] = 2

    _pathSettings = "data/settings.json"
    def loadSettings():
        if not os.path.isfile(_pathSettings):
            report("loaded")
            return
        
        file = None
        try:
            file = open(_pathSettings, "r")
            convertData.update(json.load(file))
        except:
            pass
        finally:
            if file: file.close()
            
        report("loaded")

    def saveSettings():
        report("log", "Saving settings... ")
        file = open(_pathSettings, "w")
        json.dump(convertData, file)
        file.close()
        report("log", "Done\n")

    convertEvent = threading.Event()
    convertData = dict()
    convertThread = threading.Thread(target=threadConvert, daemon=True)
    convertThread.start()
    
    window.update()
    loadSettings()
    setConvertData()
    reloadInputFile()

    window.mainloop()

if __name__ == "__main__":
    main()
