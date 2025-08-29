from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GraphicBuildType(Enum):
    """
    Indicates how graphic display style during animation.
    
    Attributes:
        BuildAsOne: The entire graphic is built as one object.
        BuildAsSeries: The graphic is built by series.
        BuildAsCategory: The graphic is built by category.
        BuildAsSeriesElement: The graphic is built by series elements.
        BuildAsCategoryElement: The graphic is built by category elements.
    """
    BuildAsOne = 0
    BuildAsSeries = 1
    BuildAsCategory = 2
    BuildAsSeriesElement = 3
    BuildAsCategoryElement = 4

