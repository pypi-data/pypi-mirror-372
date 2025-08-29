from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class DataLabelShapeType(Enum):
    """
    Specifies the shape type used for data labels in charts.
    """
    none = 0
    Rectangle = 1
    RoundedRectangle = 2
    Oval = 3
    RightArrowCallout = 4
    DownArrowCallout = 5
    LeftArrowCallout = 6
    UpArrowCallout = 7
    RectangularCallout = 8
    RoundedRectangularCallout = 9
    OvalCallout = 10
    LineCallout1 = 11
    LineCallout2 = 12
    AccentCallout1 = 13
    AccentCallout2 = 14

