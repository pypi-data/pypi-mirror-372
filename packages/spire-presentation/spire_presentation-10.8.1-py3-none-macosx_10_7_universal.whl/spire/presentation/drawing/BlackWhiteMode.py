from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlackWhiteMode(Enum):
    """
    Specifies color transformation modes to black and white.
    
    Attributes:
        none (int): No transformation. Value: -1.
        Color (int): Retain original colors. Value: 0.
        Auto (int): Automatic transformation. Value: 1.
        Gray (int): Gray scale transformation. Value: 2.
        LightGray (int): Light gray transformation. Value: 3.
        InverseGray (int): Inverse gray transformation. Value: 4.
        GrayWhite (int): Gray and white transformation. Value: 5.
        BlackGray (int): Black and gray transformation. Value: 6.
        BlackWhite (int): Black and white transformation. Value: 7.
        Black (int): Pure black transformation. Value: 8.
        White (int): Pure white transformation. Value: 9.
        Hidden (int): Hide the shape. Value: 10.
    """
    none = -1
    Color = 0
    Auto = 1
    Gray = 2
    LightGray = 3
    InverseGray = 4
    GrayWhite = 5
    BlackGray = 6
    BlackWhite = 7
    Black = 8
    White = 9
    Hidden = 10

