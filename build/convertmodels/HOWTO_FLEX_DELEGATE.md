## Windows

> [!WARNING]
> This howto is untested and i was not able to get it to work
> It was intended to reduce the file size for built windows releases

1. Install and boot Windows VM (optional, if you already are on a Windows 10+ Machine)
2. `winget install -e --id Python.Python.3.11`
3. `pip3 install -U six numpy wheel packaging`
4. `pip3 install -U keras_preprocessing --no-deps`
5. `winget install -e --id Bazel.Bazel --version 7.3.1`
6. `winget install -e --id MSYS2.MSYS2`
7. `set PATH=C:\msys64\usr\bin;%PATH%`
8. `pacman -Syu`
9. `pacman -S git patch unzip`
10. `pacman -S git patch unzip rsync`
11. `winget install -e --id Microsoft.VisualStudio.2019.BuildTools --override "--wait --passive --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.19041"` (I had to manually install the Windows 10 SDK by opening Visual Studio Installer, through the Windows Search -> Modify -> Components -> Windows 10 SDK (19041) -> Click Modify)
12. `winget install -e --id Microsoft.VCRedist.2015+.x86`
13. `winget install -e --id LLVM.LLVM`
14. `set PATH=C:\Program Files\LLVM\bin;%PATH%`
15. `set BAZEL_LLVM=C:\Program Files\LLVM`
14. `git clone --branch v2.18.0 --depth 1 https://github.com/tensorflow/tensorflow`
15. `cd tensorflow`
16. `bazel sync --repo_env=TF_PYTHON_VERSION=3.11`
16. `bazel build -c opt --config=monolithic --config=windows --config=win_clang --repo_env=TF_PYTHON_VERSION=3.11 tensorflow/lite/delegates/flex:tensorflowlite_flex`