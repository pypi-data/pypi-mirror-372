from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextUnderlineType(Enum):
    """
    Represents the type of text underline.

    Attributes:
        UnDefined: Undefined underline type.
        none: No underline.
        Words: Words underline.
        Single: Single underline.
        Double: Double underline.
        Heavy: Heavy underline.
        Dotted: Dotted underline.
        HeavyDotted: Heavy dotted underline.
        Dashed: Dashed underline.
        HeavyDashed: Heavy dashed underline.
        LongDashed: Long dashed underline.
        HeavyLongDashed: Heavy long dashed underline.
        DotDash: Dot-dash underline.
        HeavyDotDash: Heavy dot-dash underline.
        DotDotDash: Dot-dot-dash underline.
        HeavyDotDotDash: Heavy dot-dot-dash underline.
        Wavy: Wavy underline.
        HeavyWavy: Heavy wavy underline.
        DoubleWavy: Double wavy underline.
    """
    UnDefined = -1
    none = 0
    Words = 1
    Single = 2
    Double = 3
    Heavy = 4
    Dotted = 5
    HeavyDotted = 6
    Dashed = 7
    HeavyDashed = 8
    LongDashed = 9
    HeavyLongDashed = 10
    DotDash = 11
    HeavyDotDash = 12
    DotDotDash = 13
    HeavyDotDotDash = 14
    Wavy = 15
    HeavyWavy = 16
    DoubleWavy = 17

