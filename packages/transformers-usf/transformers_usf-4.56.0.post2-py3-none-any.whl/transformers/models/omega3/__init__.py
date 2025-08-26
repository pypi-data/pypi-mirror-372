from typing import TYPE_CHECKING

from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure


if TYPE_CHECKING:
    from .configuration_omega3 import *
    from .image_processing_omega3 import *
    from .image_processing_omega3_fast import *
    from .modeling_omega3 import *
    from .processing_omega3 import *
else:
    import sys

    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)
