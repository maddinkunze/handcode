import os
import re
import sys
import math
import subprocess

sys.path.append("lib") # for clean build reasons we dont include lib.handwriting
import handwriting

filename = "demo.txt"  # filename of the input file, should be located within the data subdirectory (if converttype == "file")
saveext = "nc"         # extension of the output file (will be located within the data subdirectory)
                       # e.g. filename="test.txt" and saveext="nc" -> output file will be "test.nc"
                       # should only ever be a variant of gcode, so "gcode", "nc" (estlcam)

pendown = 0  # z-location when the pen is down/pressed
penup = 6    # z-location when the pen is up/released
feedrate = 2000  # movement feedrate for both travel and writing

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

alphabet = handwriting.alphabet
replacetable = {
  "Q": "O",
  "X": "x",
  "Z": "z",
  "Ä": "A",
  "Ö": "O",
  "Ü": "U",
  "ä": "a",
  "ö": "o",
  "ü": "u"
}

HAND = None

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
  _offsetCountX = 7  # TODO should be dependent on number of lines (more lines -> more random dots on the side)
  _offsetCountY = 1  # and (max) number of characters each line is wide AND also maybe should be customizable(?)
  offsetsX = []
  offsetsY = []
  def _insertoffset(offsets, newoffset, maxoffsets, compare):
    if not newoffset:
      return
    newoffset = float(newoffset[0])
    if len(offsets) < maxoffsets:
      offsets.append(newoffset)
      return
    
    maxoffset = max(offsets)
    if compare(maxoffset, newoffset):
      offsets.append(newoffset)
      offsets.remove(maxoffset)
  def _getoffset(offsets):
    if not offsets:
      return 0

    # basically returning the median
    numoffsets = len(offsets)
    _i = int(numoffsets / 2)
    if numoffsets % 2:
      return offsets[_i]
    else:
      return (offsets[_i-1] + offsets[_i]) / 2
      
  patternX = re.compile("X(-?[0-9]*\.?[0-9]*)(?:$|\s)")
  patternY = re.compile("Y(-?[0-9]*\.?[0-9]*)(?:$|\s)")

  for line in data:
    # remove lines that only move the head to the top
    if line.startswith("G0") and "X0" in line:
      continue

    # get top-most position
    if line.startswith("G0") or line.startswith("G1"):
      currentX = patternX.findall(line)
      _insertoffset(offsetsX, currentX, _offsetCountX, lambda old, new: old > new)
      currentY = patternY.findall(line)
      _insertoffset(offsetsY, currentY, _offsetCountY, lambda old, new: old < new)

    # swapping x and y axis
    if swapXY:
      line = line.replace("X", "__T").replace("Y", "X").replace("__T", "Y")

    # append clean line again
    dataClean.append(line)

  offsetX = _getoffset(offsetsX) # get median
  offsetY = _getoffset(offsetsY) # get median

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

def initializehandwritingengine():
  global HAND
  _engine = handwriting.Hand
  if isinstance(HAND, _engine):
    return
  HAND = _engine()

def converttohandwriting(filein, fileout, bias=0.75, style=12):
  file = open(filein, "r")
  data = file.read().split("\n")
  file.close()

  biases = [bias for l in data]
  styles = [style for l in data]
  widths = [0.1 for l in data]

  if data and any(map(str.strip, data)):  # if there are lines that contain anything other than a null character
    HAND.write(filename=fileout, lines=data, biases=biases, styles=styles, stroke_widths=widths)
  else:
    return 0
  return len(data)

def converttogcode(filein, fileout, height=10, feedrate=300, penup=5, pendown=0):
  path_svg2gcode = os.path.abspath(os.path.join(os.curdir, "lib", "svg2gcode", "svg2gcode.exe"))
  command_svg2gcode = f"{path_svg2gcode} --dimensions ,{height}mm --feedrate {feedrate} --on \"G0 Z{pendown}\" --off \"G0 Z{penup}\" --out {fileout} {filein}"

  si = subprocess.STARTUPINFO()
  si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
  subprocess.call(command_svg2gcode, startupinfo=si)

def splittextfile(filein, filesout):
  file = open(filein, "r")
  lines = file.read().split("\n")
  file.close()
  
  files = [open(file, "w") for file in filesout]

  for i, line in enumerate(lines):
    fi = i % len(files)
    if i >= len(files):  # if we are not on the first line of the current file, append a newline to the last line -> no unneccessary \n characters
      files[fi].write("\n")
    elif not line:
      line = " "  # force content on every files first line, otherwise distances may be messed up
    files[fi].write(line)

  for file in files:
    file.close()

def replaceinvalidcharacters(filein, fileout, alphabet=alphabet, replacetable={}):
  file = open(filein, "r")
  lines = file.read().split("\n")
  file.close()

  _countindexstart = 1  # should the output be formatted like "on line 1, word 2" (1-indexed) or "on line 0, word 1" (0-indexed)
  _safechar = " "  # safe character if no replacement rule is given
  if _safechar not in alphabet:
    _safechar = ""
    
  replacements = []
  cleanedtext = ""
  
  for lineno, line in enumerate(lines, _countindexstart):
    if lineno > _countindexstart:
      cleanedtext += "\n"
      
    for wordno, word in enumerate(line.split(" "), _countindexstart):
      if wordno > _countindexstart:
        cleanedtext += " "

      wordreplacements = []
      for oldchar in word:
        newchar = oldchar

        while newchar not in alphabet: # doing this allows for multiple replacements of the same character, eg Ü -> U -> V if neither Ü nor U exist
          newchar = replacetable.get(newchar, _safechar)
          if newchar == _safechar:
            break
          
        if newchar != oldchar:
          wordreplacements.append((oldchar, newchar))

        cleanedtext += newchar

      if wordreplacements:
        replacements.append(((lineno, wordno), word, wordreplacements))

  file = open(fileout, "w")
  file.write(cleanedtext)
  file.close()

  return replacements


def convert(filename, saveext, pendown, penup, feedrate, fontsize, fontstyle, fontbias, swapXY, linespernewline, alphabet, replacetable, log=None):
  if not log:
    log = lambda s: print(s, end="")
    
  log("Preparing data... ")
  if not os.path.exists("temp"):
    os.mkdir("temp")
  if not os.path.exists("data"):
    os.mkdir("data")
  filein = os.path.join("data", filename)
  fileintemp = os.path.join("temp", os.path.split(filein)[-1])
  fileinsplit = os.path.join("temp", "input{}.txt")
  filehandwriting = os.path.join("temp", "handwriting{}.svg")
  filegcode = os.path.join("temp", "handwriting{}.gcode")
  filencode = os.path.join("temp", "handwriting{}.nc")
  _split = "."
  _fn, _ext = filename.rsplit(_split, 1)
  fileout = os.path.join("data", _fn + _split + saveext)

  replacedcharacters = replaceinvalidcharacters(filein, fileintemp, alphabet, replacetable)
  splittextfile(fileintemp, [fileinsplit.format(i) for i in range(linespernewline)])
  log("Done\n")

  log("Initializing handwriting engine... ")
  initializehandwritingengine()
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
    converttogcode(filehandwriting.format(i), filegcode.format(i), height=fontsize*numlines, feedrate=feedrate, penup=penup, pendown=pendown)
    log("Done\n")

    log(f"[File {i+1}/{linespernewline}] Simplifying gcode... ")
    offsetTop = (0.95 * i + 0.05) * fontsize  # TODO the 0.95 is a weird hack, should be customizable (?) [Line height factor] or something
    simplifygcode(filegcode.format(i), filencode.format(i), swapXY=swapXY, offsetTop=offsetTop)
    log("Done\n")

  log("Merging gcode files...")
  mergegcode([filencode.format(i) for i in range(linespernewline)], fileout)
  log("Done\n")
  
  log("All done :)\n")

  if replacedcharacters:
    log("\nThe following characters were replaced:\n")
    for position, word, replacements in replacedcharacters:
      log(f"On line {position[0]}, word {position[1]} = {word}:\n")
      for oldchar, newchar in replacements:
        log(f" - [{oldchar}] -> [{newchar}]\n")
  

if __name__ == "__main__":
  convert(filename, saveext, pendown, penup, feedrate, fontsize, fontstyle, fontbias, swapXY, linespernewline, alphabet, replacetable)
