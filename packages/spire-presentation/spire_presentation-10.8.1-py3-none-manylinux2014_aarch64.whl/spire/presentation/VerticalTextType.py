from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class VerticalTextType(Enum):
    """
    Specifies vertical writing modes for text.
    
    Attributes:
        none: No vertical text
        Horizontal: Regular horizontal text
        Vertical: Vertical text (top-to-bottom)
        Vertical270: Vertical text (bottom-to-top)
        WordArtVertical: WordArt vertical text
        EastAsianVertical: East Asian vertical text
        MongolianVertical: Mongolian vertical text
        WordArtVerticalRightToLeft: WordArt vertical right-to-left
    """
    none = -1
    Horizontal = 0
    Vertical = 1
    Vertical270 = 2
    WordArtVertical = 3
    EastAsianVertical = 4
    MongolianVertical = 5
    WordArtVerticalRightToLeft = 6

