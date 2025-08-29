from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationRepeatType(Enum):
    """
    Specifies the timing repeat type for animations.
    
    Attributes:
        Number: Repeat a specific number of times.
        UtilNextClick: Repeat until next click.
        UtilEndOfSlide: Repeat until end of slide.
    """
    Number = 0
    UtilNextClick = 1
    UtilEndOfSlide = 2

