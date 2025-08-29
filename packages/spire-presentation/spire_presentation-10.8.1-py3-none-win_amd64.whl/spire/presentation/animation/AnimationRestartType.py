from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationRestartType(Enum):
    """
    Specifies when an animation effect restarts.
    
    Attributes:
        none: No restart specified.
        Always: Always restarts.
        WhenOff: Restarts when turned off.
        Never: Never restarts.
    """
    none = -1
    Always = 0
    WhenOff = 1
    Never = 2

