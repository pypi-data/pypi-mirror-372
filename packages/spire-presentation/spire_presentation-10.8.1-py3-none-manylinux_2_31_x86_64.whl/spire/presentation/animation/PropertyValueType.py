from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PropertyValueType(Enum):
    """
    Specifies the data type of a property value in presentation elements.
    
    Attributes:
        none (-1): Uninitialized or undefined property value type
        String (0): Property value is a text string
        Number (1): Property value is a numerical value
        Color (2): Property value specifies a color
    """
    none = -1
    String = 0
    Number = 1
    Color = 2

