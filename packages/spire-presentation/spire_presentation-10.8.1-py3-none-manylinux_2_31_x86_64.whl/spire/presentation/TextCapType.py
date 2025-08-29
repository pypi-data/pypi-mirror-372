from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextCapType(Enum):
    """
    Represents the type of text capitalisation.
    
    Attributes:
        UnDefined: Undefined capitalization type
        none: No capitalization applied
        Small: Small capital letter formatting
        All: All uppercase formatting
    """
    UnDefined = -1
    none = 0
    Small = 1
    All = 2

