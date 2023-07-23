# HandCode - A handwiriting gcode generator

## Overview

HandCode is a simple tool that enables its users to automatically create GCode from plain text input. This GCode can then be used to, for example, build a handwriting robot.

## How to Use

![](doc/process.png)

### Options

#### File Options

##### Filename:

This is the name (and path) of the text file, whose content will be used for the synthesis. If it is located within the data subdirectory it will simply show the filename, otherwise the whole path will be displayed. You can select your own text files or write in the large text input below to change the data that will be converted to gcode.
> :warning: **Warning**: If you are editing after opening a text file, starting the conversion process will write the changes in the opened file. This may lead to data loss so please verify you are editing the correct file before each conversion.

##### Export extension:

This is the extension that will be used for the export file. The export content will always be GCode, but some programs (i.e. Estlcam) require the file extension to be .nc, so to avoid the renaming step after each conversion you can use this field.

#### Font Options

##### Size:

This is the "font" size of the generated text. In theory it should be the line height in mm, so if you have paper with lines spaced 15mm apart from each other, the font size should be 15mm. However in practice, it has been more reliable to simply trial and error this value.

##### Style:

This is the handwriting sample used. The project is based on a neural network for handwriting synthesis for which 12 people have submitted samples of their handwriting. You can choose between those 12 or create your own handwriting sample.
You can test out all 12 handwriting samples in a [web demo](https://www.calligrapher.ai/).

##### Legibility:

Honestly, i don't really know what exactly this does, i just copied its description from the [web demo](https://www.calligrapher.ai/). It should be a value between 0 and 1.

#### Pen Options

#### Other Options

## Features

This project is based on great work from Sean Vasquez, who published his work on handwriting synthesis. It ensures the uniqueness of each letter and the natural flow from each letter to the next. You can choose between 12 sampled handwritings or (if you _really_ want to, i dont know how though) sample your own handwriting to use with this program.

## Contributions

This project is written in [Python](https://python.org) and uses the following projects:
 - [svg2gcode](https://github.com/sameer/svg2gcode)
 - [handwriting-synthesis](https://github.com/sjvasquez/handwriting-synthesis)