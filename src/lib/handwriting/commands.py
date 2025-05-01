import typing

_CommandItem = str|typing.Callable[[], str]|None
class _MoveCommand(typing.TypedDict):
    start: _CommandItem
    move: _CommandItem
    end: _CommandItem
class _PageCommand(typing.TypedDict):
    start: _CommandItem
    next: _CommandItem
    end: _CommandItem
class CommandDict(typing.TypedDict):
    draw: _MoveCommand
    travel: _MoveCommand
    page: _PageCommand

def gcode(pendraw=0, pentravel=5, penpause=50, feeddraw=1000, feedtravel=1000) -> CommandDict:
    return {
        "draw": {
            "start": None,
            "move": f"G1 X{{x:f}} Y{{y:f}} Z{pendraw} F{feeddraw}\n",
            "end": None,
        },
        "travel": {
            "start": None,
            "move": f"G0 X{{x:f}} Y{{y:f}} Z{pentravel} F{feedtravel}\n",
            "end": None
        },
        "page": {
            "start": None,
            "next": f"G0 Z{penpause} F{feedtravel}\nM0\n",
            "end": f"G0 Z{penpause} F{feedtravel}\n"
        }
    }

def gcode_laser(pendraw=0, pentravel=5, penpause=50, feeddraw=1000, feedtravel=1000, speeddraw=None, speedtravel=None):
    return {
        "draw": {
            "start": f"M3 S{pendraw}",
            "move": f"G1 X{{x:f}} Y{{y:f}} F{feeddraw}\n",
            "end": None,
        },
        "travel": {
            "start": f"M5" if pentravel is None else f"M3 S{pentravel}",
            "move": f"G0 X{{x:f}} Y{{y:f}} F{feedtravel}\n",
            "end": None
        },
        "page": {
            "start": None,
            "next": (f"M5" if penpause is None else f"M3 S{penpause}") + f"M0\n",
            "end": f"M5" if penpause is None else f"M3 S{penpause}"
        }
    }

def svg(pendraw=None, pentravel=None, penpause=None, feeddraw=None, feedtravel=None) -> CommandDict:
    return {
        "draw": {
            "start": None,
            "move": lambda x, y, **_: f"L {x:f} {-y:f} ",
            "end": None,
        },
        "travel": {
            "start": None,
            "move": lambda x, y, **_: f"M {x:f} {-1*y:f} ",
            "end": None,
        },
        "page": {
            "start": "<!DOCTYPE svg><svg xmlns=\"http://www.w3.org/2000/svg\"><g><path d=\"",
            "next": "\" style=\"fill:none;stroke:green;stroke-width:1;stroke-linejoin:round;stroke-linecap:round;\" /></g><g><path d=\"",
            "end": "\" style=\"fill:none;stroke:green;stroke-width:1;stroke-linejoin:round;stroke-linecap:round;\" /></g></svg>"
        }
    }