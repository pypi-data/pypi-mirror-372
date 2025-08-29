from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FontCollectionIndex(Enum):
    """
    Specifies font indexes within a font collection.
    
    Attributes:
        none: Not part of a font collection.
        Minor: Font for body text sections.
        Major: Font for heading sections.
    """
    none = 0
    Minor = 1
    Major = 2

