from enum import Enum
from typing import Literal, Annotated, Union, Callable, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from handwriting.formats import GCodeHandler

class _FormatsSettings(BaseModel):
    type: str
    def to_format_handler(self):
        pass


class _GCodeMoveCommand(BaseModel):
    type: str
    def to_command_handler(self): ...

class _BaseGCodeMove(_GCodeMoveCommand):
    arg_pos_x: str = Field(default="X", description="Name of the argument that is used to set the X position (i.e. 'X' -> `G0 X10 ...` to move to 10 along the x axis)")
    arg_pos_y: str = Field(default="Y", description="Name of the argument that is used to set the Y position (i.e. 'Y' -> `G0 Y5 ...` to move to 5 alogn the y axis)")
    arg_feedrate: str = Field(default="F", description="Name of the argument that is used to set the feedrate for this move (i.e. 'F' -> `G0 F200` to set the feedrate to 200 mm/s)")
    commands_start: tuple[str] = Field(default=(), description="GCode commands to add at the start of a sequence of moves of this same type")
    commands_between: tuple[str] = Field(default=(), description="GCode commands to add between two moves of this same type")
    commands_end: tuple[str] = Field(default=(), description="GCode commands to add at the end of a sequence of moves of this same type")
    commands_before: tuple[str] = Field(default=(), description="GCode commands to add before this move command")
    commands_after: tuple[str] = Field(default=(), description="GCode commands to add after this move command")

class GCodeMove(_BaseGCodeMove):
    type: Literal["move"] = "move"
    command: str = Field()
    feedrate: float = Field()

class GCodeLaserMove(_BaseGCodeMove):
    type: Literal["laser"] = "laser"
    command_move: str = Field()
    command_power: str = Field(default="M3")
    feedrate: float = Field()
    arg_power: str = Field(default="O")
    power_start: int = Field()
    power_end: int|None = Field()

class GCodePlungeMove(_BaseGCodeMove):
    type: Literal["plunge"] = "plunge"
    command: str = Field()
    z_start: float = Field()
    z_end: float|None = Field(default=None)
    arg_pos_z: str = Field(default="Z")
    feedrate_move: float = Field()
    feedrate_plunge: float = Field()

class GCodeMillMove(_BaseGCodeMove):
    type: Literal["mill"] = "mill"
    command_move: str = Field()
    command_mill: str = Field(default="M3")
    z_start: float = Field()
    z_end: float|None = Field(default=None)
    arg_pos_z: str = Field(default="Z")
    arg_speed: str = Field(default="S")
    speed_start: int = Field()
    speed_end: int|None = Field(default=None)
    feedrate_move: float = Field()
    feedrate_plunge: float = Field()

GCodeMoveCommands = Annotated[Union[
    GCodeLaserMove,
    GCodePlungeMove,
    GCodeMillMove,
], Field(discriminator="type")]

class GCodeSettings(_FormatsSettings):
    type: Literal["gcode"] = "gcode"
    move: GCodeMoveCommands = Field(default=GCodeMove(command="G0", feedrate=500))
    draw: GCodeMoveCommands = Field(default=GCodePlungeMove(command="G1", feedrate_move=200, feedrate_plunge=500, z_start=0, z_end=5))

class SVGSettings(_FormatsSettings):
    type: Literal["svg"] = "svg"


FormatsSettings = Annotated[Union[
    GCodeSettings,
    SVGSettings,
], Field(discriminator="type")]
