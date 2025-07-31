from pathlib import Path
from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field

class _InputSettings(BaseModel):
    type: str

class TextSettings(_InputSettings):
    type: Literal["text"]
    text: str

class FileSettings(_InputSettings):
    type: Literal["file"]
    path: Path

InputSettings = Annotated[Union[
    TextSettings,
    FileSettings,
], Field(discriminator="type")]
