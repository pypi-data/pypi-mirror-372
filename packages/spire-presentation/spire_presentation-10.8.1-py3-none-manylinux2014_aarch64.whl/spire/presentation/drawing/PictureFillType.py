from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PictureFillType(Enum):
    """
    Specifies how a picture should fill its target area.
    
    Enumeration Members:
        Tile (0): The picture is repeated to fill the area (tiled).
        Stretch (1): The picture is stretched to fill the entire area.
    """
    Tile = 0
    Stretch = 1

