from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextStrikethroughType(Enum):
    """
    Enum representing text strikethrough types.
    
    Attributes:
        UnDefined: Undefined strikethrough
        none: No strikethrough
        Single: Single line strikethrough
        Double: Double line strikethrough
    """
    UnDefined = -1
    none = 0
    Single = 1
    Double = 2

