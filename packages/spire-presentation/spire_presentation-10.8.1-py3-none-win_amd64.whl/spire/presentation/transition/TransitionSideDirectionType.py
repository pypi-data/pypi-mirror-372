from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionSideDirectionType(Enum):
    """
    Specifies side direction types for slide transitions.
    
    Attributes:
        Left: Transition moves from the left
        Up: Transition moves from the top
        Down: Transition moves from the bottom
        Right: Transition moves from the right
    """
    Left = 0
    Up = 1
    Down = 2
    Right = 3

