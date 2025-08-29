from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationCalculationMode(Enum):
    """
    Represents calculation modes for animation properties.
    
    Attributes:
        none: No calculation mode specified.
        Discrete: Discrete calculation mode.
        Linear: Linear calculation mode.
        Formula: Formula-based calculation mode.
    """
    none = -1
    Discrete = 0
    Linear = 1
    Formula = 2

