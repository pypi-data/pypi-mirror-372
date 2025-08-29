from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextVerticalOverflowType(Enum):
    """
    Represents text vertical overflow type.

    Attributes:
        none: No overflow.
        Overflow: Overflow behavior.
        Ellipsis: Ellipsis behavior.
        Clip: Clip behavior.
    """
    none = -1
    Overflow = 0
    Ellipsis = 1
    Clip = 2

