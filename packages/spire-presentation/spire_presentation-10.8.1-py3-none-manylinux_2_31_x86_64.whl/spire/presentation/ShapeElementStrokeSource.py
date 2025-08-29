from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeElementStrokeSource(Enum):
    """
    Specifies how a shape element should be stroked.
    
    Attributes:
        NoStroke: Element should not have an outline.
        Shape: Inherit stroke from parent shape.
        OwnStroke: Use element's own stroke properties.
    """
    NoStroke = 0
    Shape = 1
    OwnStroke = 2

