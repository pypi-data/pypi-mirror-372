from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDisplayUnitType(Enum):
    """
    Specifies the unit of measurement for displaying chart values.
    
    Attributes:
        none:No scaling - display actual values.
        Hundreds:Display values in hundreds.
        Thousands:Display values in thousands.
        TenThousands:Display values in ten thousands.
        HundredThousands:Display values in hundred thousands.
        Millions:Display values in millions.
        TenMillions:Display values in ten millions.
        HundredMillions:Display values in hundred millions.
        Billions:Display values in billions.
        Trillions:Display values in trillions.
        Percentage:Display values as percentages.
    """
    none = 0
    Hundreds = 1
    Thousands = 2
    TenThousands = 3
    HundredThousands = 4
    Millions = 5
    TenMillions = 6
    HundredMillions = 7
    Billions = 8
    Trillions = 9
    Percentage = 10

