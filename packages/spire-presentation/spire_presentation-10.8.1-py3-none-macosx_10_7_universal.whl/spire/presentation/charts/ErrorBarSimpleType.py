from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ErrorBarSimpleType(Enum):
    """
    Specifies the direction of error bars in charts.
    
    Attributes:
        Both: Shows error bars in both positive and negative directions.
        Minus: Shows error bars only in negative direction.
        Plus: Shows error bars only in positive direction.
    """
    Both = 0
    Minus = 1
    Plus = 2

