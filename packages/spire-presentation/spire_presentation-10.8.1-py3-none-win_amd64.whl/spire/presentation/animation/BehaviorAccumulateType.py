from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BehaviorAccumulateType(Enum):
    """
    Specifies accumulation types for effect behaviors.
    
    Attributes:
        UnDefined (int): Undefined accumulation type. Value: -1.
        Always (int): Always accumulate effects. Value: 0.
        none (int): No accumulation. Value: 1.
    """
    UnDefined = -1
    Always = 0
    none = 1

