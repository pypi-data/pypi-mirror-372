from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class VideoPlayMode(Enum):
    """
    Specifies how a video should be played during a presentation.

    Attributes:
        Mixed: Mixed play mode
        Auto: Play automatically
        OnClick: Play when clicked
        Presentation: Play as part of presentation
    """
    Mixed = -1
    Auto = 0
    OnClick = 1
    Presentation = 2

