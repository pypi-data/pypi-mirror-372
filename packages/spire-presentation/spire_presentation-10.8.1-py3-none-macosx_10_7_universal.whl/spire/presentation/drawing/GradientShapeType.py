from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientShapeType(Enum):
    """
    Defines the geometric shape used for gradient fills.

    Attributes:
        none (-1): No gradient shape defined.
        Linear (0): Gradient follows a straight line.
        Rectangle (1): Gradient radiates from a rectangle's center.
        Radial (2): Gradient radiates from a circular center point.
        Path (3): Gradient follows a custom path shape.
    """
    none = -1
    Linear = 0
    Rectangle = 1
    Radial = 2
    Path = 3

