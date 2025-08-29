from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MotionPathPointsType(Enum):
    """
    Specifies the types of points used in animation motion paths.
    
    Attributes:
        none: No specific point type.
        Auto: Automatically determined point type.
        Corner: Point represents a sharp corner in the path.
        Straight: Point connects straight path segments.
        Smooth: Point creates a smooth curved path.
        CurveAuto: Automatically determined curve point.
        CurveCorner: Curve point with sharp corner behavior.
        CurveStraight: Curve point connecting straight segments.
        CurveSmooth: Curve point creating smooth transitions.
    """
    none = 0
    Auto = 1
    Corner = 2
    Straight = 3
    Smooth = 4
    CurveAuto = 5
    CurveCorner = 6
    CurveStraight = 7
    CurveSmooth = 8

