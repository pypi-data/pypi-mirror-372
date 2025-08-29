from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TickMarkType(Enum):
    """
    Represents the tick mark type for the specified axis.
    
    Attributes:
        TickMarkNone: No tick marks
        TickMarkCross: Cross-shaped tick marks
        TickMarkInside: Tick marks inside the axis
        TickMarkOutside: Tick marks outside the axis
    """
    TickMarkNone = 0
    TickMarkCross = 1
    TickMarkInside = 2
    TickMarkOutside = 3

