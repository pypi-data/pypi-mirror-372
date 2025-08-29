from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AudioVolumeType(Enum):
    """
    Indicates audio volume levels.
    
    Attributes:
        Mixed: Mixed volume level.
        Mute: Muted volume.
        Low: Low volume.
        Medium: Medium volume.
        Loud: Loud volume.
    """
    Mixed = -1
    Mute = 0
    Low = 1
    Medium = 2
    Loud = 3

