import os

def _dictEnsurePath(d, *path):
    for p in path:
        if p not in d:
            d[p] = dict()
        d = d[p]

def formatFloat(x):
    return f"{x:f}".rstrip("0").rstrip(".")

def formatFontStyleName(i):
    return f"Style {i}"

def convertSettingsLegacyFrom030(settings):
    settingsNew = dict()
    if "filename" in settings:
        _dictEnsurePath(settingsNew, "output")
        filename = settings["filename"]
        if "saveext" in settings:
            saveext = settings["saveext"]
            filename = f"{os.path.splitext(filename)[0]}{os.path.extsep}{saveext}"
        settingsNew["output"]["file"] = filename

    if "pendown" in settings:
        _dictEnsurePath(settingsNew, "pen", "heights")
        settingsNew["pen"]["heights"]["draw"] = formatFloat(settings["pendown"])
    if "penup" in settings:
        _dictEnsurePath(settingsNew, "pen", "heights")
        settingsNew["pen"]["heights"]["travel"] = formatFloat(settings["penup"])

    if "feedrate" in settings:
        _dictEnsurePath(settingsNew, "pen", "speeds")
        settingsNew["pen"]["speeds"]["draw"] = formatFloat(settings["feedrate"])
        settingsNew["pen"]["speeds"]["travel"] = formatFloat(settings["feedrate"])

    if "fontsize" in settings:
        _dictEnsurePath(settingsNew, "font")
        settingsNew["font"]["size"] = formatFloat(settings["fontsize"])
    if "fontstyle" in settings:
        _dictEnsurePath(settingsNew, "font")
        settingsNew["font"]["style"] = formatFontStyleName(settings["fontstyle"])
    if "fontbias" in settings:
        _dictEnsurePath(settingsNew, "font")
        settingsNew["font"]["bias"] = formatFloat(settings["fontbias"] * 100)

    if "swapXY" in settings:
        _dictEnsurePath(settingsNew, "page")
        settingsNew["page"]["rotate"] = formatFloat(90 if settings["swapXY"] else 0)

    settingsNew["version"] = "0.4.0"
    return settingsNew

def convertSettingsLegacyFrom041(settings):
    settingsNew = {**settings}
    if "output" in settingsNew:
        settingsNewOut = settingsNew["output"]
        if "format" in settingsNewOut:
            formatIds = {"GCode": "gcode"}
            settingsNewOut = formatIds.get(settingsNewOut["format"], "gcode")
    if "font" in settingsNew:
        settingsNewFont = settingsNew["font"]
        if "style" in settingsNewFont:
            try:
                styleId = int(settingsNewFont["style"].split()[-1])
            except:
                styleId = 0
            settingsNewFont["style"] = styleId
    settingsNew["model"] = "cai-ulw"
    settingsNew["version"] = "0.5.0"
    return settingsNew

def convertSettingsKnownGood(newVersion):
    def _conv(settings):
        settings["version"] = newVersion
        return settings
    return _conv

_legacyVersionsSettings = {
    "0.3.0": convertSettingsLegacyFrom030,
    "0.4.0": convertSettingsKnownGood("0.4.1"),
    "0.4.1": convertSettingsLegacyFrom041,
}
def convertSettingsLegacy(settings, versionCurrent):
    versionLast = None
    while settings:
        version = settings.get("version", "0.3.0")
        if version == versionCurrent:
            break
        if version == versionLast:
            return dict()
        if version not in _legacyVersionsSettings:
            return dict()
        convertSettingsF = _legacyVersionsSettings[version]
        settings = convertSettingsF(settings)
        versionLast = version

    return settings
