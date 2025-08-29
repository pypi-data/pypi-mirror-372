from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDataLabelPosition(Enum):
    """
    Indicates position options for data labels.

    Attributes:
        Bottom:Positioned at bottom
        BestFit:Automatically determine best position
        Center:Positioned at center
        InsideBase:Positioned inside base
        InsideEnd:Positioned inside end
        Left:Positioned at left
        OutsideEnd:Positioned outside end
        Right:Positioned at right
        Top:Positioned at top
        none:No specific position
    """
    Bottom = 0
    BestFit = 1
    Center = 2
    InsideBase = 3
    InsideEnd = 4
    Left = 5
    OutsideEnd = 6
    Right = 7
    Top = 8
    none = 9

