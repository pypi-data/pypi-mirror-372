from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FilterEffectsType(Enum):
    """
    Specifies the direction of filter effects applied to slide transitions.
    
    Attributes:
        Both (int): Apply filter effects in both horizontal and vertical directions.
        Horizontal (int): Apply filter effects only in the horizontal direction.
        Vertical (int): Apply filter effects only in the vertical direction.
    """
    Both = 0
    Horizontal = 1
    Vertical = 2

