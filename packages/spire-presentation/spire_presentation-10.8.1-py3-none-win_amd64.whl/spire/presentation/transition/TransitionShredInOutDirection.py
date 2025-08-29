from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionShredInOutDirection(Enum):
    """
    Specifies the direction types for shred in/out slide transitions.
    
    Attributes:
        StripIn: Transition shreds in with strips effect
        StripOut: Transition shreds out with strips effect
        RectangleIn: Transition shreds in with rectangle effect
        RectangleOut: Transition shreds out with rectangle effect
    """
    StripIn = 0
    StripOut = 1
    RectangleIn = 2
    RectangleOut = 3

