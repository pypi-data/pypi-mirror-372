from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextHorizontalOverflowType(Enum):
    """
    Represents text horizontal overflow type.

    Attributes:
        none: No overflow handling specified.
        Overflow: Text overflows horizontally.
        Clip: Text is clipped at the boundary.
    """
    none = -1
    Overflow = 0
    Clip = 1

