from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextLineStyle(Enum):
    """
    Represents the style of a line.
    
    Attributes:
        none: No line style.
        Single: Single line style.
        ThinThin: Double line with two thin lines.
        ThinThick: Double line with thin then thick lines.
        ThickThin: Double line with thick then thin lines.
        ThickBetweenThin: Double line with thick between thin lines.
    """
    none = -1
    Single = 0
    ThinThin = 1
    ThinThick = 2
    ThickThin = 3
    ThickBetweenThin = 4

