from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BehaviorAdditiveType(Enum):
    """
    Specifies additive types for effect behaviors.
    
    Attributes:
        Undefined (int): Undefined additive type. Value: -1.
        none (int): No additive effect. Value: 0.
        Base (int): Base additive type. Value: 1.
        Sum (int): Summation additive type. Value: 2.
        Replace (int): Replacement additive type. Value: 3.
        Multiply (int): Multiplicative additive type. Value: 4.
    """
    Undefined = -1
    none = 0
    Base = 1
    Sum = 2
    Replace = 3
    Multiply = 4

