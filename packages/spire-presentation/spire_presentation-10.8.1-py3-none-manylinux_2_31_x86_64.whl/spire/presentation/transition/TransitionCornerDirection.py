from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionCornerDirection(Enum):
    """
    Specifies corner directions for slide transition effects.

    Attributes:
        LeftDown: Transition from left-bottom corner.
        LeftUp: Transition from left-top corner.
        RightDown: Transition from right-bottom corner.
        RightUp: Transition from right-top corner.
        none: No corner direction specified.
    """
    LeftDown = 0
    LeftUp = 1
    RightDown = 2
    RightUp = 3
    none = 4

