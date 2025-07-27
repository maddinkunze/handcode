import argparse
from build_common import _package_key, buildname

# Parse command line arguments
parser = argparse.ArgumentParser(description=f"{buildname} Build Script")
parser.add_argument("package", nargs="?", help="Package to build (e.g., windows-zip, macos-app, linux-appimage); you may not be able to cross-build")
parser.add_argument("--no-cleanup", action="store_true", default=False, help="Do not clean up build files after building")
parser.add_argument("--ignore-existing", action="store_true", default=False, help="Overwrite existing builds without warning")

args = parser.parse_args()

if args.package:
    import os
    os.environ[_package_key] = args.package.lower()


# Actually build the package
from build_config import pre_build_command, post_build_command, cx_action, distpath, clean_dirs, clean_files
from build_utils import check_existing_build, build_with_cxfreeze, remove_build_files

if not args.ignore_existing:
    check_existing_build(distpath)

pre_build_command()
build_with_cxfreeze(cx_action)
post_build_command()

if not args.no_cleanup:
    print("Cleaning up build files...", end="", flush=True)
    for path in clean_dirs:
        remove_build_files(path)
    for path in clean_files:
        remove_build_files(path)
    print("Done")
