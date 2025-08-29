from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionTwoDirection(Enum):
    """
    Defines glitter transition directions.
    
    Attributes:
        Left: Glitter moves to the left.
        Right: Glitter moves to the right.
    """
    Left = 0
    Right = 1

