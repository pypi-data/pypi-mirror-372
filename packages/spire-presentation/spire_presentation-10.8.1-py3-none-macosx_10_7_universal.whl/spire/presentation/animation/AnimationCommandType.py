from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationCommandType(Enum):
    """
    Represents command effect types for command effect behaviors.
    
    Attributes:
        none: No command type specified.
        Event: Event-based command.
        Call: Call command.
        Verb: Verb command.
    """
    none = -1
    Event = 0
    Call = 1
    Verb = 2

