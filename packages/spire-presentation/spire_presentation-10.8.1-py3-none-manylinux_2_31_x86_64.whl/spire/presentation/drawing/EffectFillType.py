from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectFillType(Enum):
    """
    Specifies types of fill effects that can be applied to presentation elements.
    
    Attributes:
        none: No fill effect applied.
        Remove: Fill effect that removes existing fills.
        Freeze: Fill effect that freezes the current appearance.
        Hold: Fill effect that maintains the current state.
        Transition: Fill effect used during state transitions.
    """
    none = -1
    Remove = 0
    Freeze = 1
    Hold = 2
    Transition = 3

