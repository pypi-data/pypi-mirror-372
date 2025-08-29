from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineJoinType(Enum):
    """
    Specifies how lines are joined at connection points.
    
    Attributes:
        none: No specific join style. Value: -1.
        Round: Rounded line joins. Value: 0.
        Bevel: Beveled (angled) line joins. Value: 1.
        Miter: Sharp angular line joins. Value: 2.
    """
    none = -1
    Round = 0
    Bevel = 1
    Miter = 2

