from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillFormatType(Enum):
    """
    Represents the type of fill used in presentation objects.

    Attributes:
        - UnDefined (-1): Fill type is undefined or not specified.
        - none (0): No fill is applied to the object.
        - Solid (1): Object is filled with a solid color.
        - Gradient (2): Object is filled with a gradient effect.
        - Pattern (3): Object is filled with a pattern.
        - Picture (4): Object is filled with an image.
        - Group (5): Fill is defined at the group level and inherited by child elements.
    """
    UnDefined = -1
    none = 0
    Solid = 1
    Gradient = 2
    Pattern = 3
    Picture = 4
    Group = 5

