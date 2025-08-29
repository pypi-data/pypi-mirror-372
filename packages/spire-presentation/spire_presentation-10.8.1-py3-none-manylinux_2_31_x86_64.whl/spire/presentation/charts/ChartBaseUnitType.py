from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartBaseUnitType(Enum):
    """
    Specifies the base unit type for category axis scaling.
    
    """
    Days = 0
    Months = 1
    Years = 2
    Auto = -1

