from typing import Union
import numpy as np
from numpy.typing import NDArray

Address = np.uintp
BlasInt = Union[np.int32, np.int64]
Char8   = Union[np.uint8, int]

from .source import *
__all__ = [name for name in globals().keys() if not name.startswith("_")]