from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAlignmentType(Enum):
    """
    Represents different text alignment styles.
    
    Attributes:
        none: No alignment specified.
        Left: Left alignment.
        Center: Center alignment.
        Right: Right alignment.
        Justify: Justified alignment.
        Dist: Distributed alignment.
    """
    none = -1
    Left = 0
    Center = 1
    Right = 2
    Justify = 3
    Dist = 4

