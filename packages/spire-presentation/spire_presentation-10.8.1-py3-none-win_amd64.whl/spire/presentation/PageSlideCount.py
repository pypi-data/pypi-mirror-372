from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PageSlideCount(Enum):
    """
    Specifies the number of slides to display per page in printed layouts or exports.
    Used for controlling output density in presentation exports/printing.
    """
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Six = 6
    Nine = 9

