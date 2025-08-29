from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ImportDataFormat(Enum):
    """
    Specifies the source file format for importing data.

    Attributes:
        Ppt: Microsoft PowerPoint 97-2003 format (.ppt)
        Pptx: Office Open XML Presentation format (.pptx)
        Odp: OpenDocument Presentation format (.odp)
    """
    Ppt = 0
    Pptx = 1
    Odp = 2

