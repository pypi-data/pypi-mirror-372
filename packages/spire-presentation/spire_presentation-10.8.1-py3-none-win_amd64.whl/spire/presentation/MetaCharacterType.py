from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MetaCharacterType(Enum):
    """
    Specifies different types of placeholder characters used in presentation text.
    
    Attributes:
        SlideNumer: Represents a slide number placeholder.
        DateTime: Represents a date/time placeholder with default formatting.
        GenericDateTime: Represents a generically formatted date/time placeholder.
        Footer: Represents a footer text placeholder.
        Header: Represents a header text placeholder.
        RtfFormatDateTime: Represents an RTF-formatted date/time placeholder.
    """
    SlideNumer = 0
    DateTime = 1
    GenericDateTime = 2
    Footer = 3
    Header = 4
    RtfFormatDateTime = 5

