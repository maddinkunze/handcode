from common import is_frozen
from packages import Package, LocalPackage

package: Package | None = None
if is_frozen:
    from BUILD_CONSTANTS import package # type: ignore[import-not-found]
else:
    package = LocalPackage()
