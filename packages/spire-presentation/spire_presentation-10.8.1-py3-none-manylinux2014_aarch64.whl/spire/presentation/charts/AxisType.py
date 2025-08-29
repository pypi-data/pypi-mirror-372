from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AxisType(Enum):
    """
    Specifies the type of a chart axis.
    
    Attributes:
        Auto: Automatic axis type determination.
        TextAxis: Text-based category axis.
        DateAxis: Date-based category axis.
    """
    Auto = 0
    TextAxis = 1
    DateAxis = 2

