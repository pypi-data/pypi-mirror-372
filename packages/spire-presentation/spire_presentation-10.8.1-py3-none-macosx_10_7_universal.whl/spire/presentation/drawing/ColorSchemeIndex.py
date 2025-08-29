from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ColorSchemeIndex(Enum):
    """
    Represents color indexes in a color scheme.
    """
    Dark1 = 0
    Light1 = 1
    Dark2 = 2
    Light2 = 3
    Accent1 = 4
    Accent2 = 5
    Accent3 = 6
    Accent4 = 7
    Accent5 = 8
    Accent6 = 9
    Hyperlink = 10
    FollowedHyperlink = 11

