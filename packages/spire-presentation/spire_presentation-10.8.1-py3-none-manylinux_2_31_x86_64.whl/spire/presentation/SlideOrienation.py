from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideOrienation(Enum):
    """
    Represents the slide orientation.

    Attributes:
        Landscape: Landscape orientation (value = 0)
        Portrait: Portrait orientation (value = 1)
    """
    Landscape = 0
    Portrait = 1

