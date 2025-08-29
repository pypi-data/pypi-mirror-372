from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimateType(Enum):
    """
    Animate type of text.

    Attributes:
        All:Default animation mode:Apply animation to the entire text block as a single unit.
        Word:word-level animation :Animate text word-by-word with spacing boundaries.
        Letter:Character-level animation:Animate text character-by-character for fine-grained effects.

    """
    All = 0
    Word = 1
    Letter = 2
   


