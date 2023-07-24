<img src="doc/img/icon.svg" width=50%>

# HandCode - A handwiriting gcode generator

## Overview

HandCode is a simple tool that enables its users to automatically create GCode from plain text input. This GCode can then be used to, for example, build a handwriting robot. It is based on a pretrained AI model to create the handwriting path. This leads to unique characters, a natural flow between characters and a realistic writing order.

## How to Use

![](doc/img/process.png)

### Options

#### File Options

##### Filename:

This is the name (and path) of the text file, whose content will be used for the synthesis. If it is located within the data subdirectory it will simply show the filename, otherwise the whole path will be displayed. You can select your own text files or write in the large text input below to change the data that will be converted to gcode. If you just want to write a short text in the large text input field, the filename input can be used for naming your output file. The inputted text will then be stored in a file located in the data subdirectory.
> :warning: **Warning**: If you are editing after opening a text file, starting the conversion process will apply your changes to the open file. This may lead to unexpected data loss. Please verify that you are editing the correct file before each conversion. Closing the program will discard all changes that are not yet saved.

##### Export extension:

This is the extension that will be used for the export file, the (base-)filename will be inherited from the filename field. The export content will always be GCode, but some programs (i.e. Estlcam) require the file extension to be .nc, so this field can be used to avoid the renaming step after each conversion.
Examples:
| Filename    | Exp. ext. | Exported file |
|-------------|-----------|---------------|
| demo.txt    | gcode     | demo.gcode    |
| estlcam.txt | nc 	  | estlcam.nc    |
| de.mo.txt   | gcode     | de.mo.gcode   |
| estlcam     | nc        | estlcam.nc    |

#### Font Options

##### Size:

This is the "font" size of the generated text. In theory it should be the line height in mm, so if you have paper with lines spaced 15mm apart from each other, the font size should be 15mm. However in practice, it has been more reliable to simply trial and error this value. To the best of my knowledge and testing, this scales linearly, so if you've tested and found out that for 15mm paper, the corrext font size is 30, then the font size for 30mm _should be_ 60mm.

##### Style:

This is the handwriting sample used. The project is based on a neural network for handwriting synthesis for which 12 people have submitted samples of their handwriting. You can choose between those 12 or create your own handwriting sample.
You can test out all 12 handwriting samples in a [web demo](https://www.calligrapher.ai/).

##### Legibility:

Honestly, i don't really know what exactly this does, i just copied its description from the [web demo](https://www.calligrapher.ai/). It should be a value between 0 and 1.

#### Pen Options

##### Z Up (Travel)

This is the (absolute) Z-Position (in mm) of your CNC tool head when the pen is travelling, i.e. not writing. This should not be too small, otherwise you may be drawing lines between characters.

##### Z Down (Writing)

This is the (absolute) Z-Position (in mm) of your CNC tool head when the pen should be drawing. This value should be 0 if you've levelled your CNC correctly and using a pen that does not need any pressure (e.g. fineliners). If you are using a pen that needs pressure (e.g. ball bens) you can decrease this value. For me a value of 0 is perfect for fineliners and a value of -1.5 applies enough pressure for a ball pen.

> :warning: **Warning**: If you are testing what the correct Z Down value is, i recommended to use a pen that is reasonably flexible to avoid damaging your CNC.

#### Other Options

##### Swap X/Y Axis (Rotate 90°)

This checkbox should be set if you want to mount the paper perpendicular to your CNC/3D Printer. Usually the GCode generated will write each line along the X-Axis and lines below each other along the Y-Axis. By checking this box, the GCode will move the tool head along its Y Axis while writing each line and along the X axis when going to the next line

## Features

This project is based on great work from Sean Vasquez, who published his work on handwriting synthesis (see contributions). It ensures the uniqueness of each letter and the natural flow from each letter to the next. You can choose between 12 sampled handwritings or (if you _really_ want to, i dont know how though) sample your own handwriting to use with this program.

## Contributions

This project is written in [Python](https://python.org) and uses the following projects:
 - [svg2gcode](https://github.com/sameer/svg2gcode)
 - [handwriting-synthesis](https://github.com/sjvasquez/handwriting-synthesis)