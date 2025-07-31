import sys
from pathlib import Path
from common import version_handcode


# Interfaces

class CompressionConfig:
    def compress(self, path): ...
    def decompress(self): ...

class Package:
    def start(self): ...

class Buildable:
    pname: str
    path_dist: Path
    can_build_from_host_system: bool
    def build(self): ...


# Base Implementations

class _UIPackage(Package):
    _path_icon: Path
    path_data: Path
    def prepare(self): ...

class _ServerPackage(Package):
    _path_temp: Path
    def start(self):
        pass

class _BaseCompressionConfig(CompressionConfig):
    pass

class _BaseUIPackage(_UIPackage):
    _fallback_home: str

class _CxFreezeBuildable(Buildable):
    _cx_action: str
    _path_build: Path
    def pre_build(self): ...
    def post_exe(self): ...
    def post_build(self): ...
    def build(self):
        self.pre_build()
        # TODO: invoke cx_freeze
        self.post_build()

class _BaseBuildableUIPackage(_BaseUIPackage, _CxFreezeBuildable):
    _package_os: str
    _package_ext: str
    _compression: CompressionConfig | None
    @property
    def pname(self):
        return f"{self._package_os}-{self._package_ext}"
    
    def prepare(self):
        if self._compression:
            self._compression.decompress()


# OS Specific Base Implementations

class _WindowsUIPackage(_BaseBuildableUIPackage):
    _fallback_home = Path.home() / "AppData" / "Local" / "handcode"
    _package_os = "windows"
    can_build_from_host_system = (sys.platform == "win32")

class _UnixLikeUIPackage(_BaseBuildableUIPackage):
    _fallback_home = Path.home() / ".handcode"

class _MacOsUIPackage(_UnixLikeUIPackage):
    _package_os = "macos"
    can_build_from_host_system = (sys.platform == "darwin")

class _LinuxUIPackage(_UnixLikeUIPackage):
    _package_os = "linux"
    can_build_from_host_system = (sys.platform.startswith("linux"))


# Actual Packages

class LocalPackage(_BaseUIPackage):
    _compression = None

class WindowsZipPackage(_WindowsUIPackage):
    _package_ext = "zip"

class MacOsAppPackage(_MacOsUIPackage):
    _package_ext = "app"

class LinuxAppImagePackage(_LinuxUIPackage):
    _package_ext = "appimage"

class DockerfilePackage(_ServerPackage, Buildable):
    pname = "dockerfile"
    path_dist = f"handcode-v{version_handcode}.dockerfile"
    can_build_from_host_system = True
    def build(self):
        pass # TODO
