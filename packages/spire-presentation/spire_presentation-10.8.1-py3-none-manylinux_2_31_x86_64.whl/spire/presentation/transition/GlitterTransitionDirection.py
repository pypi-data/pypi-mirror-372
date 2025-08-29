from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GlitterTransitionDirection(Enum):
    """
    Specifies the direction types for glitter slide transitions.

    Attributes:
        HexagonFromLeft (0): Hexagon pattern moves in from the left.
        HexagonFromUp (1): Hexagon pattern moves in from the top.
        HexagonFromDown (2): Hexagon pattern moves in from the bottom.
        HexagonFromRight (3): Hexagon pattern moves in from the right.
        DiamondFromLeft (4): Diamond pattern moves in from the left.
        DiamondFromUp (5): Diamond pattern moves in from the top.
        DiamondFromDown (6): Diamond pattern moves in from the bottom.
        DiamondFromRight (7): Diamond pattern moves in from the right.
    """
    HexagonFromLeft = 0
    HexagonFromUp = 1
    HexagonFromDown = 2
    HexagonFromRight = 3
    DiamondFromLeft = 4
    DiamondFromUp = 5
    DiamondFromDown = 6
    DiamondFromRight = 7

