from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionFlythroughInOutDirection(Enum):
    """
    Specifies in/out direction types for flythrough slide transitions.
    
    Attributes:
        In: Transition effect flies in
        Out: Transition effect flies out
        BounceIn: Transition effect bounces in
        BounceOut: Transition effect bounces out
    """
    In = 0
    Out = 1
    BounceIn = 2
    BounceOut = 3

