from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionSpeed(Enum):
    """
    Specifies the speed of slide transitions.
    
    Attributes:
        Fast: Fast transition speed.
        Medium: Medium transition speed.
        Slow: Slow transition speed.
        none: No transition speed (immediate transition).
    """
    Fast = 0
    Medium = 1
    Slow = 2
    none = 3

