from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TrendlinesType(Enum):
    """
    Specifies the type of trendline used in charts.
    
    Attributes:
        Exponential: Represents an exponential trendline.
        Linear: Represents a linear trendline.
        Logarithmic: Represents a logarithmic trendline.
        MovingAverage: Represents a moving average trendline.
        Polynomial: Represents a polynomial trendline.
        Power: Represents a power trendline.
    """
    Exponential = 0
    Linear = 1
    Logarithmic = 2
    MovingAverage = 3
    Polynomial = 4
    Power = 5

