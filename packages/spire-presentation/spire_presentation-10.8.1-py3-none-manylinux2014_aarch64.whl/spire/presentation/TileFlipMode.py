from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TileFlipMode(Enum):
    """
    Defines tile flipping mode.
    
    Attributes:
        UnDefined: Undefined flipping mode
        none: No flipping
        Horizontal: Horizontal flipping
        Vertical: Vertical flipping
        HorizontalAndVertical: Both horizontal and vertical flipping
    """
    UnDefined = -1
    none = 0
    Horizontal = 1
    Vertical = 2
    HorizontalAndVertical = 3

