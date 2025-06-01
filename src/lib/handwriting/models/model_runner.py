import os
import sys
import typing
import numpy as np
import traceback

_ProgressF = typing.Callable[[str, float|int, float|int], typing.Any]

class WritingStyle:
    def __init__(self, sid: int, name: str, image_path: str|None=None):
        self.id = sid
        self.name = name
        self.image_path = image_path

class ModelRunner:
    id: str
    name: str
    alphabet: list[str]
    writing_styles: list[WritingStyle]

    urls: list[tuple[str, str]]  # (name, url)
    description: str
    license: str
    short_info: str # two lines of info
    _base_url = "https://github.com/maddinkunze/handcode/tree/main/src/lib/handwriting/models/"

    def __init__(self, progress_cb: _ProgressF|None=None):
        self.progress_cb = progress_cb

    def load_libraries(self) -> None:
        pass

    def load(self) -> None:
        raise NotImplementedError()

    def invoke(self, text: list[str], biases: list[float], style: WritingStyle) -> list[list[float]]:
        raise NotImplementedError()

    @staticmethod
    def _get_info_from_readme(path_readme: str, path_license: str|None=None) -> tuple[str, str, str]:
        if not os.path.exists(path_readme):
            return "", "", ""

        with open(path_readme, "r", encoding="utf-8") as f:
            readme = f.read()

        description = readme.split("### Attribution")[1].split("### ")[0].strip()

        if path_license and os.path.exists(path_license):
            with open(path_license, "r", encoding="utf-8") as f:
                license = f.read().strip()
        else:
            license = readme.split("### License")[1].split("### ")[0].strip()

        short_info = "❓ Commercial use unknown\n⚖️ Unknown License"

        if "MIT License" in license:
            short_info = "💵 Commercial use allowed\n⚖️ MIT License"

        return description, license, short_info
    
    @classmethod
    def is_available(cls) -> bool:
        ...