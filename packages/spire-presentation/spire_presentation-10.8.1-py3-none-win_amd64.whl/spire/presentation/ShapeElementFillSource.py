from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeElementFillSource(Enum):
    """
    Specifies how a shape element should be filled.
    
    Attributes:
        NoFill: Element should not be filled.
        Shape: Inherit fill from parent shape.
        Lighten: Apply lightened fill effect.
        LightenLess: Apply less lightened fill effect.
        Darken: Apply darkened fill effect.
        DarkenLess: Apply less darkened fill effect.
        OwnFill: Use element's own fill properties.
    """
    NoFill = 0
    Shape = 1
    Lighten = 2
    LightenLess = 3
    Darken = 4
    DarkenLess = 5
    OwnFill = 6

