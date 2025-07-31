import typing
from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from handwriting.settings.formats import GCodeSettings, SVGSettings

class PageMetadata(BaseModel):
    pass

class PositionData(BaseModel):
    x: float
    y: float

class FormatHandler:
    """
    start -> start_group -> <move commands> -> end_group() -> end()

    e.g.
    - start()
      - start_group()
        - line_to(x, y)
        - move_to(x, y)
        - line_to(x, y)
        - line_to(x, y)
        - move_to(x, y)
        - ...
      - end_group()
    - next_file() / restart_file()
      - ...
    - end()
    """
    def start(self, data: PageMetadata) -> None: "Initialize the format and begin the first file"
    def end(self) -> str: "Finalize the format, finish and return the final file"

    def next_file(self, data: PageMetadata) -> str: "Finalize the format, finish and return the current file, reinitialize and begin a new empty file"
    def restart_file(self) -> None: "An alternative to `next_file()`, but the file will not actually end here. It should be treated as if the process pauses here for the user to put in a blank piece of paper/canvas/... Formats meant to control an actual machine should put a pause here and reset the tool state (if applicable); formats meant to represent the data (i.e. image formats) should create a new layer/tab/... (if available)"

    def start_group(self, name: str) -> None: "Start a new nested group (should have no real effect, just for organizational purposes, e.g. `<g>...</g>` in SVGs); should be nestable arbitrarily often"
    def end_group(self) -> None: "End the last nested group (see `start_group()` for more info)"

    def move_to(self, pos: PositionData) -> None: "Stop drawing (if not already stopped), move the pointer to the given position"
    def line_to(self, pos: PositionData) -> None: "Start drawing (if not already drawing), move the pointer to the given position"

class _BaseFormatHandler(FormatHandler):
    def __init__(self):
        self._current_file = ""

    def _write_to_file(self, content: str):
        self._current_file += content
    def _print_to_file(self, content: str):
        self._write_to_file(content + "\n")

    def _start_file(self, data: PageMetadata): ...
    def _end_file(self): ...

    def start(self, data):
        self._current_file = ""
        self._start_file(data)

    def next_file(self):
        self._end_file()
        last_file = self._current_file
        self._current_file = ""
        self._start_file()
        return last_file

    def end(self):
        self._end_file()
        last_file = self._current_file
        self._current_file = ""
        return last_file


class _GCodeMoveHandler:
    pass

class GCodeMoveHandler(_GCodeMoveHandler):
    pass

class GCodeHandler(_BaseFormatHandler):
    def __init__(self, settings: GCodeSettings):
        super().__init__()
        self.settings = settings

    

class SVGHandler(_BaseFormatHandler):
    def __init__(self, settings: SVGSettings):
        super().__init__()
        self.settings = settings
