from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Order(Enum):
    """
    Defines arrangement direction for layout elements.
    Controls sequencing direction in various presentation layouts.
    """
    Horizontal = 0
    Vertical = 1

