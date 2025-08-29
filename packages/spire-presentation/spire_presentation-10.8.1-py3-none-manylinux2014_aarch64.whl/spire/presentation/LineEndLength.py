from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineEndLength(Enum):
    """
    Determines the size of arrowheads and line terminators.
    
    Attributes:
        none: No arrowhead
        Short: Small-sized arrowhead
        Medium: Medium-sized arrowhead
        Long: Large-sized arrowhead
    """
    none = -1
    Short = 0
    Medium = 1
    Long = 2

