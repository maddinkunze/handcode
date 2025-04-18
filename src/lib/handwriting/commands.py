def gcode(pendraw=0, pentravel=5, penpause=50, feeddraw=1000, feedtravel=1000):
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

def gcode_laser(pendraw=0, pentravel=None, penpause=None, feeddraw=1000, feedtravel=1000):
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
