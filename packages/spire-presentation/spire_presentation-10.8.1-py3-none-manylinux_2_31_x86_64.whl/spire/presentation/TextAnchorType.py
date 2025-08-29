from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAnchorType(Enum):
    """
    Represents vertical alignment within a text area.
    
    Attributes:
        none: No anchor specified.
        Top: Top alignment.
        Center: Center alignment.
        Bottom: Bottom alignment.
        Justified: Justified alignment.
        Distributed: Distributed alignment.
        Right: Right alignment (special case).
        Left: Left alignment (special case).
    """
    none = -1
    Top = 0
    Center = 1
    Bottom = 2
    Justified = 3
    Distributed = 4
    Right = 5
    Left = 6

