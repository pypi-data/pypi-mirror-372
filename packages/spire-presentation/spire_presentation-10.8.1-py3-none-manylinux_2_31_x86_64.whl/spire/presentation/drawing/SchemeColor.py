from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SchemeColor(Enum):
    """
    Defines color scheme identifiers used in presentation themes.
    These values correspond to theme color slots in presentation templates.
    """
    none = -1
    Background1 = 0
    Text1 = 1
    Background2 = 2
    Text2 = 3
    Accent1 = 4
    Accent2 = 5
    Accent3 = 6
    Accent4 = 7
    Accent5 = 8
    Accent6 = 9
    Hyperlink = 10
    FollowedHyperlink = 11
    StyleColor = 12
    Dark1 = 13
    Light1 = 14
    Dark2 = 15
    Light2 = 16

