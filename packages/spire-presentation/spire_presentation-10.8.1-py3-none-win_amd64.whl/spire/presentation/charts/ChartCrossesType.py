from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartCrossesType(Enum):
    """
    Specifies where an axis crosses another axis in a chart.

    Attributes:
        AxisCrossesAtZero:Axis crosses at the zero point.
        Maximum:Axis crosses at the maximum value
        Custom:Axis crosses at a custom specified value
    """
    AxisCrossesAtZero = 0
    Maximum = 1
    Custom = 2

