from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ProjectionType(Enum):
    """
    Specifies the type of map projection used for geographic data visualization.
    
    Attributes:
        Automatic: Automatically determine the best projection type.
        Mercator: Mercator cylindrical map projection.
        Miller: Miller cylindrical map projection.
        Robinson: Robinson pseudo-cylindrical map projection.
    """
    Automatic = 0
    Mercator = 1
    Miller = 2
    Robinson = 2
