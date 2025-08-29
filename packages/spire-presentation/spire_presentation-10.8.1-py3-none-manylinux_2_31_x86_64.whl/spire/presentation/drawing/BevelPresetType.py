from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BevelPresetType(Enum):
    """
    Specifies preset types for 3D bevel effects on shapes.
    
    Attributes:
        none (int): No bevel effect. Value: -1.
        Angle (int): Angle bevel style. Value: 0.
        ArtDeco (int): Art Deco bevel style. Value: 1.
        Circle (int): Circular bevel style. Value: 2.
        Convex (int): Convex bevel style. Value: 3.
        CoolSlant (int): Cool Slant bevel style. Value: 4.
        Cross (int): Cross bevel style. Value: 5.
        Divot (int): Divot bevel style. Value: 6.
        HardEdge (int): Hard Edge bevel style. Value: 7.
        RelaxedInset (int): Relaxed Inset bevel style. Value: 8.
        Riblet (int): Riblet bevel style. Value: 9.
        Slope (int): Slope bevel style. Value: 10.
        SoftRound (int): Soft Round bevel style. Value: 11.
    """
    none = -1
    Angle = 0
    ArtDeco = 1
    Circle = 2
    Convex = 3
    CoolSlant = 4
    Cross = 5
    Divot = 6
    HardEdge = 7
    RelaxedInset = 8
    Riblet = 9
    Slope = 10
    SoftRound = 11

