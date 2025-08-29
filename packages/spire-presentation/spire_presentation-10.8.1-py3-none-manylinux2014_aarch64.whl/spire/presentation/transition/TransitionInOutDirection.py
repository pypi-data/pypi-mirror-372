from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionInOutDirection(Enum):
    """
    Specifies in or out direction types for slide transitions.
    
    Attributes:
        In: Transition effect moves in
        Out: Transition effect moves out
        none: No specific in/out direction
    """
    In = 0
    Out = 1
    none = 2

