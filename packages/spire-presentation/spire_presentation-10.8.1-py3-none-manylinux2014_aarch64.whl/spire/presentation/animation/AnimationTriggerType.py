from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationTriggerType(Enum):
    """
    Specifies the trigger type that starts an animation.

    Attributes:
        AfterPrevious: Start after previous animation completes.
        Mixed: Mixed trigger types.
        OnPageClick: Start on mouse click.
        WithPrevious: Start with previous animation.
        none: No specific trigger.
    """
    AfterPrevious = 0
    Mixed = 1
    OnPageClick = 2
    WithPrevious = 3
    none = 4

