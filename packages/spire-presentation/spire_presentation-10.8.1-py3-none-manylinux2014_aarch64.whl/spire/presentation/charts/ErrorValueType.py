from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ErrorValueType(Enum):
    """
    Specifies the calculation method for error bar values.
    
    Attributes:
        CustomErrorBars: Uses custom-defined error values.
        FixedValue: Uses a fixed value for all error bars.
        Percentage: Calculates errors as percentage of data values.
        StandardDeviation: Calculates errors using standard deviation.
        StandardError: Calculates errors using standard error.
    """
    CustomErrorBars = 0
    FixedValue = 1
    Percentage = 2
    StandardDeviation = 3
    StandardError = 4

