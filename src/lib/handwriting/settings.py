from typing import Literal
from pydantic import BaseModel, Field
from .models import ModelRunner
from .models.sjvasquez.model_base import BaseTFModel as VasquezModelRunner

class _InputSettings(BaseModel):
    type: str
    def as_text(self) -> str: ...

class TextInputSettings(_InputSettings):
    type: Literal["text"] = "text"
    text: str
    def as_text(self):
        return self.text


class _ModelSettings(BaseModel):
    type: str
    def get_runner(self) -> ModelRunner: ...

class CalligrapherModelSettings(_ModelSettings):
    type: Literal["calligrapher"] = "calligrapher"

class _VasquezModelSettings(_ModelSettings):
    def get_runner(self) -> VasquezModelRunner: ...

class VasquezRNNModelSettings(_VasquezModelSettings):
    type: Literal["sjvasquez-rnn"] = "sjvasquez-rnn"

class VasquezTFModelSettings(_VasquezModelSettings):
    type: Literal["sjvasquez-tf"] = "sjvasquez-tf"

class VasquezTFLiteModelSettings(_VasquezModelSettings):
    type: Literal["sjvasquez-tflite"] = "sjvasquez-tflite"

class AnandModelSettings(_ModelSettings):
    type: Literal["vickianand"] = "vickianand"


class FontAlignmentSettings(BaseModel):
    horizontal: float = Field(default=0)

class FontSettings(BaseModel):
    size: float
    line_height: float
    word_spacing: float
    alignment: FontAlignmentSettings


class PageSettings(BaseModel):
    width: float = Field(default=0)
    height: float = Field(default=0)
    rotation: float = Field(default=0)


class _CommandsSettings(BaseModel):
    type: str

class GCodeCommandsSettings(_CommandsSettings):
    type: Literal["gcode"] = "gcode"

class SVGCommandsSettings(_CommandsSettings):
    type: Literal["svg"] = "svg"


class _OutputSettings(BaseModel):
    type: str

class FileOutputSettings(_OutputSettings):
    type: Literal["file"] = "file"
    file: str


class FeatureReplaceSettings(BaseModel):
    enabled: bool = Field(default=True)

class FeatureImitateSettings(BaseModel):
    enabled: bool = Field(default=False)

class FeatureSplitPagesSettings(BaseModel):
    enabled: bool = Field(default=False)

class FeaturesSettings(BaseModel):
    replace: FeatureReplaceSettings
    imitate: FeatureImitateSettings
    split_pages: FeatureSplitPagesSettings


class HandwritingSettings(BaseModel):
    input: _InputSettings
    model: _ModelSettings
    font: FontSettings
    page: PageSettings
    commands: _CommandsSettings
    output: _OutputSettings
    features: FeaturesSettings
