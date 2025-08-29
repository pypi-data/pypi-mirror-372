from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TabAlignmentType(Enum):
    """
    Represents text tab alignment options.
    
    Defines how text aligns relative to tab stops in documents.
    """
    none = -1
    Left = 0
    Center = 1
    Right = 2
    Decimal = 3

