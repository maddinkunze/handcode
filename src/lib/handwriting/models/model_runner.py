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
    name: str
    alphabet: list[str]
    writing_styles: list[WritingStyle]

    def __init__(self, progress_cb: _ProgressF|None=None):
        self.progress_cb = progress_cb

    def load(self) -> None:
        raise NotImplementedError()

    def invoke(self, text: list[str], biases: list[float], style: WritingStyle) -> list[list[float]]:
        raise NotImplementedError()
