from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FontAlignmentType(Enum):
    """
    Specifies vertical alignment types for fonts.
    
    Attributes:
        none: No vertical alignment.
        Auto: Automatically determined vertical alignment.
        Top: Aligns text to the top.
        Center: Centers text vertically.
        Bottom: Aligns text to the bottom.
        Baseline: Aligns text to the baseline.
    """
    none = -1
    Auto = 0
    Top = 1
    Center = 2
    Bottom = 3
    Baseline = 4

