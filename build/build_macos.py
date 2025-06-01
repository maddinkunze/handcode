from build_generic import build_with_cxfreeze

def build_macos() -> None:
    build_with_cxfreeze("bdist_mac")

if __name__ == "__main__":
    build_macos()