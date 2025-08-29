from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationColorDirection(Enum):
    """
    Represents the direction of color animation.
    
    Attributes:
        none: No direction specified.
        Clockwise: Color changes in clockwise direction.
        CounterClockwise: Color changes in counter-clockwise direction.
    """
    none = -1
    Clockwise = 0
    CounterClockwise = 1

