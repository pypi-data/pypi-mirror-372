from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStyle(Enum):
    """
    Defines direction types for gradient fills.
    Attributes:
        none:No gradient applied.
        FromCorner1:Gradient radiates from top-left corner.
        FromCorner2:Gradient radiates from top-right corner.
        FromCorner3:Gradient radiates from bottom-right corner.
        FromCorner4:Gradient radiates from bottom-left corner.
        FromCenter:Gradient radiates from center outward.
    """
    none = -1
    FromCorner1 = 0
    FromCorner2 = 1
    FromCorner3 = 2
    FromCorner4 = 3
    FromCenter = 4

