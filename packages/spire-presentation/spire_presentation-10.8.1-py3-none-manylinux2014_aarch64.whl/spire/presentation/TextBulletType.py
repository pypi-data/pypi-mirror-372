from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextBulletType(Enum):
    """
    Represents the type of the extended bullets.
    
    Attributes:
        UnDefined: Undefined bullet type
        none: No bullet applied
        Symbol: Symbol-based bullet
        Numbered: Numbered list bullet
        Picture: Picture-based bullet
    """
    UnDefined = -1
    none = 0
    Symbol = 1
    Numbered = 2
    Picture = 3

