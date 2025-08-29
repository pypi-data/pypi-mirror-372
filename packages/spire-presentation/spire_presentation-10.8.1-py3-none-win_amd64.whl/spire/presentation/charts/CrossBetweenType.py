from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CrossBetweenType(Enum):
    """
    Specifies how chart axes cross between categories.

    Attributes:
        Between:Axis crosses between categories
        MidpointOfCategory:Axis crosses at midpoint of categories
    """
    none = 0
    Between = 0
    MidpointOfCategory = 1

