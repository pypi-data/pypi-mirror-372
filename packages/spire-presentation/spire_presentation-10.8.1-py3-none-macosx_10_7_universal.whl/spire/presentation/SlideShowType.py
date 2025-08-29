from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideShowType(Enum):
    """
    Specifies the presentation display mode for slide shows.
    
    Attributes:
        Present: Standard presentation mode (value: 0)
        Browse: Browsing mode (value: 1)
        Kiosk: Self-running kiosk mode (value: 2)
    """
    Present = 0
    Browse = 1
    Kiosk = 2

