from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LightingDirectionType(Enum):
    """
    Specifies the direction of light sources in 3D scenes.

    This enumeration defines possible directions from which light can illuminate 3D objects in presentations.
    """
    none = -1
    TopLeft = 0
    Top = 1
    TopRight = 2
    Right = 3
    BottomRight = 4
    Bottom = 5
    BottomLeft = 6
    Left = 7

