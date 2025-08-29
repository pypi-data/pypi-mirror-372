from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartLegendPositionType(Enum):
    """
    Indicates the position of legend on a chart.

    Attributes:
        none:
        Bottom:Legend positioned at bottom
        Left:Legend positioned at left
        Right:Legend positioned at right
        Top:Legend positioned at top
        TopRight:Legend positioned at top-right
    """
    none = -1
    Bottom = 0
    Left = 1
    Right = 2
    Top = 3
    TopRight = 4

