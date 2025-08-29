from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartShapeType(Enum):
    """
    Represents the shape type of a chart.

    Attributes:
        none:
        Box:Box shape.
        Cone:Cone shape.
        ConeToMax:Cone shape scaled to maximum value.
        Cylinder:Cylinder shape.
        Pyramid:Pyramid shape.
        PyramidToMaximum:Pyramid shape scaled to maximum value.
    """
    none = -1
    Box = 0
    Cone = 1
    ConeToMax = 2
    Cylinder = 3
    Pyramid = 4
    PyramidToMaximum = 5

