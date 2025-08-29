from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TriState(Enum):
    """
    Represents triple boolean values.
   
    """
    Null = -1
    TFalse = 0
    TTrue = 1

