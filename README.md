<p align="center"><img src="doc/img/icon.svg" width="20%"></p>

# HandCode - A handwiriting GCode generator

## Overview

HandCode is a simple tool that enables its users to automatically create GCode from plain text input. This GCode can then be used to, for example, build a handwriting robot. It is based on a pretrained AI model to create the handwriting path. This leads to unique characters, a natural flow between characters and a realistic writing order.

<p align="center"><img src="doc/img/example_handcode_drawn.jpg" width="50%"></p>

## How to Use

![](doc/img/diagram_process.png)

### Getting started

#### Preparations

First of all, you need to have an 3-axis gantry controlled by GCode. Common examples for this are CNCs, 3D printers, laser cutters or engravers. You should have some experience in using your machine and you should know what GCode is.
You also have to either clone the repo or download a release of this program (duh).
Lastly, it is recommended that you build a toolholder that can firmly hold your pen. I designed a parametrized and customizable pen holder that originally was designed to be used in a standard 3018 CNC mill, but can be adapted to many different sizes. The files for this penholder can be found [here](doc/files).

<p align="center"><img src="doc/img/machine_penholders.jpg" width="50%"></p>

#### Using HandCode

Install HandCode by downloading the latest release or by following the guide below. Open HandCode and wait until the neural network finished loading, this may take a few minutes. While waiting, you can take the text you want to convert to handwriting and save it in a plain text file. After the program finished loading you can open your text file by clicking the `...` button. If you want, you can change the settings (see below for all options) or edit your input if you noticed a mistake. After editing, changes will be saved to the file. Probably the most interesting options are the font options, which can be tested in this [web demo](https://caligrapher.ai). Note, that the font size setting is not accurate and does not represent any real life metric. See "Calibrating" below for more information.

After changing the settings to your liking you can click `Start` to start the conversion process. During this process, command prompts may open. These are for converting the handwriting to gcode and should not concern you. Please do not close them manually, they should close themselves.

When the program finishes converting, which may take a few minutes, you can use its generated GCode which is located in the `data` subdirectory.

<p align="center"><img src="doc/img/example_handcode_path.png" width="70%"></p>

#### Working with the generated GCode

The generated GCode can be saved on an SD-Card or loaded into a GCode Sender program such as [Estlcam](https://www.estlcam.de/). Before running the GCode you should zero your tool/pen to the top left of where you want your text to start. The starting point should not be at the very limits of your machine as it may move slightly beyond the zero position. Also, make sure that the lines on the paper are parallel to your X Axis. After starting the program you should stay close to the machine to ensure it does not break or move out of bounds.

<p align="center"><img src="doc/img/example_handcode_drawn.jpg" width="70%"><br><img src="doc/img/machine_3018_full.jpg" width="47%">&nbsp;<img src="doc/img/machine_3018_closeup.jpg" width="47%"></p>

#### Calibrating and Testing different values

I recommend spending some time to calibrate the font size to different line heights for your environment. To do so, simply take a text file with 10 lines of content and convert it to GCode with different font sizes. You can then measure the actual distance and graph and inter-/extrapolate it to whatever font size you might need in the future.
Furthermore i encourage you to play around with the other options, such as how high you have to lift the pen and how low you have to put it to write but not drag unneccessarily.
All options available are described below.


### Options

#### File Options

##### Filename:

This is the name (and path) of the text file, whose content will be used for the synthesis. If it is located within the data subdirectory it will simply show the filename, otherwise the whole path will be displayed. You can select your own text files or write in the large text input below to change the data that will be converted to gcode. If you just want to write a short text in the large text input field, the filename input can be used for naming your output file. The inputted text will then be stored in a file located in the data subdirectory.
> :warning: **Warning**: If you are editing after opening a text file, starting the conversion process will apply your changes to the open file. This may lead to unexpected data loss. Please verify that you are editing the correct file before each conversion. Closing the program will discard all changes that are not yet saved.

##### Export extension:

This is the extension that will be used for the export file, the (base-)filename will be inherited from the filename field. The export content will always be GCode, but some programs (i.e. Estlcam) require the file extension to be .nc, so this field can be used to avoid the renaming step after each conversion.

_Examples:_

| Filename    | Export ext. | Exported file |
|-------------|-------------|---------------|
| demo.txt    | gcode       | demo.gcode    |
| estlcam.txt | nc 	    | estlcam.nc    |
| de.mo.txt   | gcode       | de.mo.gcode   |
| otherext    | ext         | otherext.ext  |

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

This checkbox should be set if you want to mount the paper perpendicular to your CNC/3D Printer. Usually the GCode generated will write each line along the X-Axis and lines below each other along the Y-Axis. By checking this box, the GCode will move the tool head along its Y Axis while writing each line and along the X axis when going to the next line.

<p align="center"><img src="doc/img/setting_swapxy_no.jpg" width="40%">&nbsp;<img src="doc/img/setting_swapxy_yes.jpg" width="40%"></p>

## Features

This project is based on great work from Sean Vasquez, who published his work on handwriting synthesis (see attributions). It ensures the uniqueness of each letter and the natural flow from each letter to the next. You can choose between 12 sampled handwritings or (if you _really_ want to, i dont know how though) sample your own handwriting to use with this program.

## Installation

For installing HandCode you have the following options:

### Release

Head to the release section and download the latest binary for your platform.
At the moment, there are only binaries for Windows available.

### Source

1. Clone this repository, either using `git` (`git clone https://github.com/maddinkunze/handcode`) or by downloading it manually (top left, Code -> Download as zip)
2. Install `python3` for your platform (see https://python.org for more info). After this step, you should be able to call `python3 --version` from your terminal or command line (sometimes you only need to call `python --version`, but make sure it returns a `3.x.x` version). This version will be called the global python installation and be referenced as `python3`. If your python installation is called using `python`, adapt the following calls accordingly
3. Ensure `pip` (`python3 -m ensurepip`) and install `uv` (`python3 -m pip install uv`)
4. Sync dependencies (`python3 -m uv sync`), this may take some time when doing it at first
5. Activate virtual environment (`source .venv/bin/activate` on macOS and Linux, `.venv\Scripts\activate` on Windows). You should now see that your terminal has changed slightly to indicate that you are now acting from within the venv. Within your venv, you should have a new local python installation, which will be referenced from now on as just `python` (without the 3). To exit the venv, you can always call `deactivate`
6. Start HandCode (`python src/main.py` on macOS and Linux, `python src\main.py` on Windows), you should now see the program starting

## Building

For building this project you need to do the following:

### Windows

You should be simply able to run the `build.bat` script provided in the `build` subdirectory. Besides the libraries you installed for the project you need to install build libraries such as [cx_Freeze](https://cx-freeze.readthedocs.io/en/stable/). You can install all needed libraries using `python3 -m uv pip install -r build\requirements.txt --python .venv\Scripts\python.exe`. Note, that you have to install the `requirements.txt` that is located within the `build` directory and you have to call `build.bat` with the virtual environment activated and whilst `build` directory. The `--python .venv\Scripts\python.exe` flag ensures, that the build requirements are installed into the virtual environment and not into your global python installation; you may have to change the location of your venv executable.

For completeness, here is a complete rundown of what you need to do, to build HandCode for Windows:
1. Follow instructions for installation (source code); verify that the program starts and works without problems
2. Make sure, you are at the project root (`cd C:\path\to\handcode`)
3. Steps 4-5 are optional, if you have already installed the build tools in your virtual environment
4. Make sure, you are outside of your virtual environment (you can leave your venv using `deactivate`)
5. Install build requirements (`python3 -m uv pip install -r build\requirements.txt --python .venv\Scripts\python.exe`)
6. Activate virtual environment (`.venv\Scripts\activate`)
7. Go into `build` directory (`cd build`)
8. Start the build process (`build.bat`); this will take some time
9. Follow the instructions during the build, they are required to minimize the build size
9. Optional: Package the built folder into a single zip file for distribution

The provided script will do the following:
1. Build and bundle the software to the best of cx_Freeze's capabilities, see [cx_Freezes documentation](https://cx-freeze.readthedocs.io/en/stable/) and my `build/setup.py` script for more information
2. Add files (and folders) cx_Freeze did not copy correctly (mainly files from tensorflow since cx_Freeze somehow misses a few and i dont know how to force cx_Freeze to include the whole tensorflow library)
3. Remove unneccessary files, especially library data, demos, tests, duplicate files and folders, especially pycache folders. This step is not strictly needed but it reduces the package size from initially ~400-500MB to 300MB (still very big but meh)

### Other

I have not tested nor built this project on other platforms then mentioned. If you wish to build this for other platforms, you have to include the [svg2gcode binary](https://github.com/sameer/svg2gcode/releases/) for your platform in the `src/lib/svg2gcode` subdirectory and change the `os.system(...)` call in `converttogcode(...)` within `src/convert.py` to point to your platform-specific binary.


## Attributions

This project is written in [Python](https://python.org) and uses the following project:
 - [handwriting-synthesis](https://github.com/sjvasquez/handwriting-synthesis) (No License, but use like this seems to be in reasonable scope)

Previous versions used to rely on the following project:
 - [svg2gcode](https://github.com/sameer/svg2gcode) (MIT License)
