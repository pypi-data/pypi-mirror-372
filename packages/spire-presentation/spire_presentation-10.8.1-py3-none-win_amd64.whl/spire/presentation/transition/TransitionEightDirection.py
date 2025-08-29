from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionEightDirection(Enum):
    """
    Specifies eight possible directions for slide transitions.
    
    Attributes:
        LeftDown: Transition moves from left-down direction
        LeftUp: Transition moves from left-up direction
        RightDown: Transition moves from right-down direction
        RightUp: Transition moves from right-up direction
        Left: Transition moves from left
        Up: Transition moves from top
        Down: Transition moves from bottom
        Right: Transition moves from right
        none: No specific direction
    """
    LeftDown = 0
    LeftUp = 1
    RightDown = 2
    RightUp = 3
    Left = 4
    Up = 5
    Down = 6
    Right = 7
    none = 8

