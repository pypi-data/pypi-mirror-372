from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PresetShadowValue(Enum):
    """
    Defines the types of preset shadow effects available for presentation elements.
    
    These enumerated values represent different preconfigured shadow effects that
    can be applied to shapes, text, and other slide objects.
    """
    TopLeftDrop = 0
    TopLeftLargeDrop = 1
    BackLeftLongPerspective = 2
    BackRightLongPerspective = 3
    TopLeftDoubleDrop = 4
    BottomRightSmallDrop = 5
    FrontLeftLongPerspective = 6
    FrontRightLongPerspective = 7
    OuterBox3D = 8
    InnerBox3D = 9
    BackCenterPerspective = 10
    TopRightDrop = 11
    FrontBottom = 12
    BackLeftPerspective = 13
    BackRightPerspective = 14
    BottomLeftDrop = 15
    BottomRightDrop = 16
    FrontLeftPerspective = 17
    FrontRightPerspective = 18
    TopLeftSmallDrop = 19

