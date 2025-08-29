from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineEndType(Enum):
    """
    Specifies the style of arrowheads at line ends.
    
    Attributes:
        UnDefined: Undefined arrowhead type. Value: -1.
        none: No arrowhead. Value: 0.
        TriangleArrowHead: Standard triangular arrowhead. Value: 1.
        StealthArrow: Stealth (angled) arrowhead. Value: 2.
        Diamond: Diamond-shaped arrowhead. Value: 3.
        Oval: Oval-shaped arrowhead. Value: 4.
        NoEnd: No end decoration. Value: 5.
    """
    UnDefined = -1
    none = 0
    TriangleArrowHead = 1
    StealthArrow = 2
    Diamond = 3
    Oval = 4
    NoEnd = 5

