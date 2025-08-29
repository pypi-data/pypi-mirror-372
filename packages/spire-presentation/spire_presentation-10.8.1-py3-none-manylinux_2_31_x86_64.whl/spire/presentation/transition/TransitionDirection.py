from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionDirection(Enum):
    """
    Specifies basic direction types for slide transitions.
    
    Attributes:
        Horizontal: Horizontal transition direction
        Vertical: Vertical transition direction
        none: No specific direction
    """
    Horizontal = 0
    Vertical = 1
    none = 2

