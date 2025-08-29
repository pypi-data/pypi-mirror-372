from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAutofitType(Enum):
    """
    Represents text autofit mode.
    
    Attributes:
        UnDefined: Undefined autofit mode
        none: No autofit applied
        Normal: Standard autofit behavior
        Shape: Shape-based autofit behavior
    """
    UnDefined = -1
    none = 0
    Normal = 1
    Shape = 2

