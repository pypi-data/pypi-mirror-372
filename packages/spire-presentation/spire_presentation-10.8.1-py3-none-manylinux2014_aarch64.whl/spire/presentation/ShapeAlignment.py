from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeAlignment(Enum):
    """
    Represents different alignment options for shapes.

    This enumeration provides options for aligning and distributing shapes 
    within a slide or container.

    Values:
        AlignLeft: Align shapes to the leftmost position.
        AlignCenter: Align shapes to the horizontal center.
        AlignRight: Align shapes to the rightmost position.
        AlignTop: Align shapes to the topmost position.
        AlignMiddle: Align shapes to the vertical middle.
        AlignBottom: Align shapes to the bottom position.
        DistributeVertically: Distribute shapes evenly along the vertical axis.
        DistributeHorizontally: Distribute shapes evenly along the horizontal axis.
    """
    AlignLeft = 0
    AlignCenter = 1
    AlignRight = 2
    AlignTop = 3
    AlignMiddle = 4
    AlignBottom = 5
    DistributeVertically = 6
    DistributeHorizontally = 7

