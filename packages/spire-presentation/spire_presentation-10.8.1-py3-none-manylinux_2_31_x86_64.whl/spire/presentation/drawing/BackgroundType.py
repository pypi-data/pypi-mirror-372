from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BackgroundType(Enum):
    """
    Specifies slide background fill types.
    
    Attributes:
        none (int): No background fill. Value: -1.
        Themed (int): Theme-defined background. Value: 0.
        Custom (int): Custom-defined background. Value: 1.
    """
    none = -1
    Themed = 0
    Custom = 1

