from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class InsertPlaceholderType(Enum):
    """

    """
    Content = 0
    VerticalContent = 1
    Text = 2
    VerticalText = 3
    Picture = 4
    Chart = 5
    Table = 6
    SmartArt = 7
    Media = 8
    OnlineImage = 9
