from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TreeMapLabelOption(Enum):
    """
    Defines label positioning options for TreeMap charts.
    
    Attributes:
        none: No labels displayed.
        Banner: Labels displayed in banners.
        Overlapping: Labels displayed overlapping data points.
    """
    none = 0
    Banner = 1
    Overlapping = 2

