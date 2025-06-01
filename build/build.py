import sys

if sys.platform == "win32":
    from build_win import build_win
    build_win()
elif sys.platform == "darwin":
    from build_macos import build_macos
    build_macos()
else:
    print("/--------------------------------------------------------------------------------\\")
    print("| WARNING! No matching build platform found, trying to build generic distribtion |")
    print("\\--------------------------------------------------------------------------------/")
    print()
    from build_generic import build_generic
    build_generic()