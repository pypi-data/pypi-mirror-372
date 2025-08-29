from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MotionCommandPathType(Enum):
    """
    Defines command types for animation motion path segments.
    
    Attributes:
        MoveTo: Represents a move-to command (reposition without drawing)
        LineTo: Represents a straight line path segment
        CurveTo: Represents a curved path segment (Bezier)
        CloseLoop: Closes the current path loop
        End: Terminates the path definition
    """
    MoveTo = 0
    LineTo = 1
    CurveTo = 2
    CloseLoop = 3
    End = 4

