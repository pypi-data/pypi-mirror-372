from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationColorspace(Enum):
    """
    Represents color space for color effect behaviors.
    
    Attributes:
        none: No color space specified.
        RGB: RGB color space.
        HSL: HSL color space.
    """
    none = -1
    RGB = 0
    HSL = 1

