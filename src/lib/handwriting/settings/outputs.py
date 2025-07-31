from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field

class _OutputSettings(BaseModel):
    type: str

class StdoutSettings(_OutputSettings):
    type: Literal["stdout"] = "stdout"

OutputSettings = Annotated[Union[
    StdoutSettings,
], Field(discriminator=type)]
