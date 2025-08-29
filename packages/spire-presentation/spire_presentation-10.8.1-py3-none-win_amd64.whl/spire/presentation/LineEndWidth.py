from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineEndWidth(Enum):
    """
    Specifies the width of an arrowhead at the end of a line.
    
    Attributes:
        none: No arrowhead width. Value: -1.
        Narrow: Narrow arrowhead width. Value: 0.
        Medium: Medium arrowhead width. Value: 1.
        Wide: Wide arrowhead width. Value: 2.
    """
    none = -1
    Narrow = 0
    Medium = 1
    Wide = 2

