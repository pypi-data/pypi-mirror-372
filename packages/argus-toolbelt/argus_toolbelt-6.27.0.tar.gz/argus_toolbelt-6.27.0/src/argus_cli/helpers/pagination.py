from typing import Callable
import warnings
from argus_api.pagination import (
    LimitOffsetPaginator,
)  # exposed here for backward compatibility
from argus_api.pagination import offset_paginated as _offset_paginated


def offset_paginated(func: Callable) -> Callable:
    warnings.warn(
        "offset_paginated has been moved to the argus_api package and will be removed from argus_cli.",
        category=DeprecationWarning,
    )
    return _offset_paginated(func)
