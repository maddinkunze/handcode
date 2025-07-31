from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field

class _FeatureSettings(BaseModel):
    name: str
    enabled: bool = Field(default=True)

class RotateLinesFeatureSettings(_FeatureSettings):
    name: Literal["rotate-lines"] = "rotate-lines"

class RotatePageFeatureSettings(_FeatureSettings):
    name: Literal["rotate-page"] = "rotate-page"

class LineWrapFeatureSettings(_FeatureSettings):
    name: Literal["wrap-lines"] = "wrap-lines"

class HardLimitsFeatureSettings(_FeatureSettings):
    name: Literal["hard-limits"] = "hard-limits"

class SmoothStrokesFeatureSettings(_FeatureSettings):
    name: Literal["smooth-strokes"] = "smooth-strokes"

class ReplaceFeatureSettings(BaseModel):
    name: Literal["replace-characters"] = "replace-characters"
    imitate: bool = Field(default=False)
    imitate_diaresis_as_macron: bool = Field(default=False)

FeatureSettings = Annotated[Union[
    RotateLinesFeatureSettings,
    RotatePageFeatureSettings,
    LineWrapFeatureSettings,
    HardLimitsFeatureSettings,
    SmoothStrokesFeatureSettings,
    ReplaceFeatureSettings,
], Field(discriminator="name")]


class _DefaultFeaturesFactory:
    _default_features: tuple[FeatureSettings] | None = None
    @classmethod
    def get_default_features(cls):
        if cls._default_features is None:
            cls._default_features = (
                ReplaceFeatureSettings(),
                SmoothStrokesFeatureSettings(),
            )
        return cls._default_features
    
def get_default_features():
    return _DefaultFeaturesFactory.get_default_features()
