from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BevelColorType(Enum):
    """
    Specifies the color mode for 3D bevel effects on shapes.
    
    Attributes:
        Contour (int): Color applied to contour lines. Value: 0.
        Extrusion (int): Color applied to extrusion surfaces. Value: 1.
    """
    Contour = 0
    Extrusion = 1

