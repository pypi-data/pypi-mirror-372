from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNodePresetClassType(Enum):
    """
    Specifies the classification type of animation effects in presentation timing nodes.
    
    Attributes:
        none: No specific effect class.
        Entrance: Entrance animation effects.
        Exit: Exit animation effects.
        Emphasis: Emphasis animation effects.
        Path: Motion path animation effects.
        Verb: Action verb animation effects.
        MediaCall: Media-specific animation effects.
    """
    none = 0
    Entrance = 1
    Exit = 2
    Emphasis = 3
    Path = 4
    Verb = 5
    MediaCall = 6

