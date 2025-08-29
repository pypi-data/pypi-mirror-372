from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FilterRevealType(Enum):
    """
    Represents reveal behavior for filter effects.
    
    Attributes:
        UnDefined: Undefined reveal behavior.  
        none: No reveal effect applied.  
        In: Reveal effect moving inward.
        Out: Reveal effect moving outward.
    """
    UnDefined = -1
    none = 0
    In = 1
    Out = 2

