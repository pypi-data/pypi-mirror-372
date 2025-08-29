from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationMotionOrigin(Enum):
    """
    Indicates the origin point of a motion path animation.
    
    Attributes:
        none: No origin specified.
        Parent: Motion relative to parent container.
        Layout: Motion relative to slide layout.
    """
    none = -1
    Parent = 0
    Layout = 1

