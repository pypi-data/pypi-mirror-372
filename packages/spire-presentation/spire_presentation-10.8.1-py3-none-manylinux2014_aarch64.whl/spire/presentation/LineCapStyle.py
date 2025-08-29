from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineCapStyle(Enum):
    """
    Defines the decoration applied to the ends of lines.
    
    Attributes:
        none: No line cap (system default)
        Round: Rounded line ends
        Square: Square line ends extending beyond endpoint
        Flat: Flat line ends at endpoint (butt cap)
    """
    none = -1
    Round = 0
    Square = 1
    Flat = 2

