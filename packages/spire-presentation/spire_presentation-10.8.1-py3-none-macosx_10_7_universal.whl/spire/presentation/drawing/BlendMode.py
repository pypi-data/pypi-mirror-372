from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlendMode(Enum):
    """
    Specifies the blend mode for visual effects.
    
    Attributes:
        Darken (int): Darken blend mode. Value: 0.
        Lighten (int): Lighten blend mode. Value: 1.
        Multiply (int): Multiply blend mode. Value: 2.
        Overlay (int): Overlay blend mode. Value: 3.
        Screen (int): Screen blend mode. Value: 4.
        none (int): No blend mode applied. Value: 5.
    """
    Darken = 0
    Lighten = 1
    Multiply = 2
    Overlay = 3
    Screen = 4
    none = 5

