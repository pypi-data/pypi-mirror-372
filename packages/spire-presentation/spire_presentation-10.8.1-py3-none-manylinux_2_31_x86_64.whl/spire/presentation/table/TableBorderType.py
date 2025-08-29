from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TableBorderType(Enum):
    """
    Represents table border styles.
    
    Enumeration Members:
        none: No border
        All: All borders
        Inside: Inside borders only
        Outside: Outside borders only
        ToggleTop: Toggle top border
        ToggleBottom: Toggle bottom border
        ToggleLeft: Toggle left border
        ToggleRight: Toggle right border
        InsideHorizontal: Inside horizontal borders
        InsideVertical: Inside vertical borders
        DiagonalDown: Diagonal down border
        DiagonalUp: Diagonal up border
    """
    none = 1
    All = 2
    Inside = 4
    Outside = 8
    ToggleTop = 16
    ToggleBottom = 32
    ToggleLeft = 64
    ToggleRight = 128
    InsideHorizontal = 256
    InsideVertical = 512
    DiagonalDown = 1024
    DiagonalUp = 2048

