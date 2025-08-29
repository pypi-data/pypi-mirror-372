from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionRevealLRDirection(Enum):
    """
    Specifies the direction types for reveal left/right slide transitions.
    
    Attributes:
        SmoothlyFromLeft: Transition reveals smoothly from the left
        SmoothlyFromRight: Transition reveals smoothly from the right
        TroughBlackFromLeft: Transition reveals through black from the left
        TroughBlackFromRight: Transition reveals through black from the right
    """
    SmoothlyFromLeft = 0
    SmoothlyFromRight = 1
    TroughBlackFromLeft = 2
    TroughBlackFromRight = 3

