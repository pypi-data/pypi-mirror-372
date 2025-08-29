from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class RectangleAlignment(Enum):
    """
    Specifies the alignment position of a rectangular object.
    
    Defines 9-point alignment positions for rectangular objects within a containing space.
    """
    none = -1
    TopLeft = 0
    Top = 1
    TopRight = 2
    Left = 3
    Center = 4
    Right = 5
    BottomLeft = 6
    Bottom = 7
    BottomRight = 8

