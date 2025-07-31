import typing
from pydantic import BaseModel
if typing.TYPE_CHECKING:
    from lib.handwriting.settings import HandwritingSettings
else:
    from handwriting.settings import HandwritingSettings

class PackageSettings(BaseModel):
    pass

class HandCodeSettings(BaseModel):
    package: PackageSettings
    handwriting: HandwritingSettings
