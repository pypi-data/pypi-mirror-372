from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PictureType(Enum):
    """
    Specifies how an image fills chart bars.

    Enumeration Members:
        none: No picture filling
        Stack: Stacks images to fill bars
        StackScale: Stacks and scales images to fill bars
        Stretch: Stretches a single image to fill bars
    """
    none = -1
    Stack = 0
    StackScale = 1
    Stretch = 2

