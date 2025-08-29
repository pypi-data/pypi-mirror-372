from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ColorType(Enum):
    """
    Specifies the type of color representation in a presentation.
    
    Attributes:
        none: Represents an undefined color type.
        RGB: Color defined by Red, Green, Blue components.
        HSL: Color defined by Hue, Saturation, Luminance components.
        Scheme: Color from the presentation's theme scheme.
        System: System-defined color (OS-level color definitions).
        KnownColor: Predefined named colors from a known colors list.
    """
    none = -1
    RGB = 0
    HSL = 1
    Scheme = 3
    System = 4
    KnownColor = 5

