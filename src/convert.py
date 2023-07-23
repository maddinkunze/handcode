import os
import re
import math
from handwriting import Hand

filename = "demo.txt"  # filename of the input file, should be located within the data subdirectory (if converttype == "file")
saveext = "nc"         # extension of the output file (will be located within the data subdirectory)
                       # e.g. filename="test.txt" and saveext="nc" -> output file will be "test.nc"
                       # should only ever be a variant of gcode, so "gcode", "nc" (estlcam)

pendown = 0  # z-location when the pen is down/pressed
penup = 6    # z-location when the pen is up/released

# the following settings can be tested in the online handwriting generator demo:
# https://www.calligrapher.ai/
fontsize = 14.18  # size of one line of generated text (does not strictly follow any metric but should roughly match the entered value in millimeters)
                  # should be determined via trial and error
fontstyle = 3     # style of the handwriting as determined by the handwriting generation package
                  # can be anything between 1-12 (at the time of writing)
fontbias = 0.75   # "legibility" of the generated handwriting, dont know what that means, but you can play with it in the online demo

swapXY = True        # if the paper is mounted 90deg to the machine, X and Y axis may need to be swapped (technically rotated but meh)
linespernewline = 2  # generating handwriting leaves an empty line after every content line, so to circumvent this we split the input file
                     # and generate the handwriting for every odd and even line seperately and merge those afterwards to effectively use every line
                     # should only ever be 1 or 2, but feel free to play with it


def mergegcode(files, fileout):
  fileo = open(fileout, "w")

  for file in files:
    filei = open(file, "r")
    fileo.write(filei.read())
    filei.close()

  fileo.close()

def simplifygcode(filein, fileout, swapXY=False, offsetTop=0, offsetLeft=0):
  file = open(filein, "r")
  data = file.read().split("\n")
  file.close()

  dataClean = []
  offsetX = None
  offsetY = None
  patternX = re.compile("X(-?[0-9]*\.?[0-9]*)(?:$|\s)")
  patternY = re.compile("Y(-?[0-9]*\.?[0-9]*)(?:$|\s)")

  for line in data:
    # remove lines that only move the head to the top
    if line.startswith("G0") and "X0" in line:
      continue

    # get top-most position
    if line.startswith("G0") or line.startswith("G1"):
      currentX = patternX.findall(line)
      if currentX:
        currentX = float(currentX[0])
      else:
        currentX = offsetX

      if (offsetX is None) or (currentX < offsetX):
        offsetX = currentX

      currentY = patternY.findall(line)
      if currentY:
        currentY = float(currentY[0])
      else:
        currentY = offsetY

      if (offsetY is None) or (currentY > offsetY):
        offsetY = currentY

    # swapping x and y axis
    if swapXY:
      line = line.replace("X", "__T").replace("Y", "X").replace("__T", "Y")

    # append clean line again
    dataClean.append(line)

  if offsetX is None:
    offsetX = 0
  if offsetY is None:
    offsetY = 0

  offsetX += offsetLeft
  offsetY += offsetTop
  if swapXY:
    offsetX, offsetY = offsetY, offsetX
  
  file = open(fileout, "w")
  for line in dataClean:
    # align origin to top (remove unneccessary space)
    if line.startswith("G0") or line.startswith("G1"):
      currentX = patternX.findall(line)
      if currentX:
        currentX = currentX[0]
      else:
        currentX = 0

      # align origin to left (remove unneccessary space)
      currentY = patternY.findall(line)
      if currentY:
        currentY = currentY[0]
      else:
        currentY = 0

      newX = (float(currentX)-offsetX) * (1-2*swapXY)
      newY = (float(currentY)-offsetY)
      line = line.replace(f" X{currentX}", f" X{newX}").replace(f" Y{currentY}", f" Y{newY}")

    file.write(line)
    file.write("\n")
  file.close()

def converttohandwriting(filein, fileout, bias=0.75, style=12):
  file = open(filein, "r")
  data = file.read().split("\n")
  file.close()

  biases = [bias for l in data]
  styles = [style for l in data]
  widths = [0.1 for l in data]

  if data and any(data):
    Hand().write(filename=fileout, lines=data, biases=biases, styles=styles, stroke_widths=widths)
  else:
    return 0
  return len(data)

def converttogcode(filein, fileout, height=10, feedrate=300, penup=5, pendown=0):
  path_svg2gcode = os.path.join(os.curdir, "lib", "svg2gcode", "svg2gcode.exe")
  os.system(f"{path_svg2gcode} --dimensions ,{height} --feedrate {feedrate} --on \"G0 Z{pendown}\" --off \"G0 Z{penup}\" --out {fileout} {filein}")

def splittextfile(filein, filesout):
  file = open(filein, "r")
  lines = file.read().split("\n")
  file.close()
  
  files = [open(file, "w") for file in filesout]

  for i, line in enumerate(lines):
    fi = i % len(files)
    if i >= len(files):
      files[fi].write("\n")
    files[fi].write(line)

  for file in files:
    file.close()


def convert(filename, saveext, pendown, penup, fontsize, fontstyle, fontbias, swapXY, linespernewline, log=None):
  if not log:
    log = lambda s: print(s, end="")
    
  log("Preparing data... ")
  if not os.path.exists("temp"):
    os.mkdir("temp")
  if not os.path.exists("data"):
    os.mkdir("data")
  filein = os.path.join("data", filename)
  fileinsplit = os.path.join("temp", "input{}.txt")
  filehandwriting = os.path.join("temp", "handwriting{}.svg")
  filegcode = os.path.join("temp", "handwriting{}.gcode")
  filencode = os.path.join("temp", "handwriting{}.nc")
  _split = "."
  _fn, _ext = filename.rsplit(_split, 1)
  fileout = os.path.join("data", _fn + _split + saveext)

  splittextfile(filein, [fileinsplit.format(i) for i in range(linespernewline)])
  log("Done\n")

  for i in range(linespernewline):
    log(f"[File {i+1}/{linespernewline}] Converting to handwriting... ")
    numlines = converttohandwriting(fileinsplit.format(i), filehandwriting.format(i), fontbias, fontstyle)
    if not numlines:
      log("Done (empty)\n")
      open(filencode.format(i), "w").close()  # make sure output file is empty
      continue
    log("Done\n")

    log(f"[File {i+1}/{linespernewline}] Converting to gcode... ")
    numlines += (numlines+1) * (linespernewline-1) # add "empty" lines (e.g. 5 lines with content will have 4 lines without content between them and 1 above and below, so together 5+4+2=11 logical lines)
    converttogcode(filehandwriting.format(i), filegcode.format(i), height=fontsize*numlines, feedrate=2000, penup=penup, pendown=pendown)
    log("Done\n")

    log(f"[File {i+1}/{linespernewline}] Simplifying gcode... ")
    offsetTop = 0.9 * i * fontsize
    simplifygcode(filegcode.format(i), filencode.format(i), swapXY=swapXY, offsetTop=offsetTop)
    log("Done\n")

  log("Merging gcode files...")
  mergegcode([filencode.format(i) for i in range(linespernewline)], fileout)
  log("Done\n")
  
  log("All done :)\n")
  

if __name__ == "__main__":
  convert(filename, saveext, pendown, penup, fontsize, fontstyle, fontbias, swapXY, linespernewline)
