from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeArrange(Enum):
    """
    Represents arrangement operations for shapes in a z-order stack.

    This enumeration provides options for changing the stacking order
    of overlapping shapes.

    Attributes:
        BringToFront: Bring the shape to the front of all other shapes.
        SendToBack: Send the shape behind all other shapes.
        BringForward: Move the shape one level forward in the z-order.
        SendBackward: Move the shape one level backward in the z-order.
    """
    BringToFront = 0
    SendToBack = 1
    BringForward = 2
    SendBackward = 3

