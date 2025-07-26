from build_generic import build_with_cxfreeze

def build_linux() -> None:
    build_with_cxfreeze("bdist_appimage")

if __name__ == "__main__":
    build_linux()