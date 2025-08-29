from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class InteriorColorPattern(Enum):
    """
    Specifies shading patterns used for shape fills.
    """
    Auto = 0
    Checker = 1
    CrissCross = 2
    Down = 3
    Gray16 = 4
    Gray25 = 5
    Gray50 = 6
    Gray75 = 7
    Gray8 = 8
    Grid = 9
    Horizontal = 10
    LightDown = 11
    LightHorizontal = 12
    LightUp = 13
    LightVertical = 14
    LinearGradient = 15
    none = 16
    RectangularGradient = 17
    SemiGray75 = 18
    Solid = 19
    Up = 20
    Vertical = 21

