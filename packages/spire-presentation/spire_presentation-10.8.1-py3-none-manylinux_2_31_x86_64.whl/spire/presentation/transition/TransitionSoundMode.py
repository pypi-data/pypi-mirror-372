from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionSoundMode(Enum):
    """
    Defines sound behavior during slide transitions.
    
    Attributes:
        none: No sound effect.
        StartSound: Start sound with transition.
        StopPrevoiusSound: Stop previous sound and start new sound.
    """
    none = -1
    StartSound = 0
    StopPrevoiusSound = 1

