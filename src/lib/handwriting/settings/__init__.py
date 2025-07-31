from pydantic import BaseModel, Field

from .inputs import InputSettings
from .models import ModelSettings
from .formats import FormatsSettings, GCodeSettings
from .outputs import OutputSettings, StdoutSettings
from .features import FeatureSettings, get_default_features

class HandwritingSettings(BaseModel):
    input: InputSettings
    model: ModelSettings
    commands: FormatsSettings = Field(default_factory=GCodeSettings)
    output: OutputSettings = Field(default_factory=StdoutSettings)
    features: tuple[FeatureSettings] = Field(default_factory=get_default_features)
