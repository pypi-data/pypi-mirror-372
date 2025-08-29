from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class QuartileCalculation(Enum):
    """
    Defines the method used for calculating quartiles in Box and Whisker charts.
    
    This enumeration determines how quartiles are calculated when generating Box and Whisker chart statistics.
    """
    InclusiveMedian = 0
    ExclusiveMedian = 1

