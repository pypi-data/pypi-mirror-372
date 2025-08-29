from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class DisplayBlanksAsType(Enum):
    """
    Indicates how missing data will be displayed.
    
    """
    Gap = 0
    Span = 1
    Zero = 2

