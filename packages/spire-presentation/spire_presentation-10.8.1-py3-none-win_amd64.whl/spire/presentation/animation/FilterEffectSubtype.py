from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FilterEffectSubtype(Enum):
    """
    Represents specific variations of filter effects for slide transitions.
    
    Attributes:
        none (int): No specific subtype applied. 
        Across (int): Effect applied across the slide.
        Down (int): Effect applied downward direction.
        DownLeft (int): Effect applied diagonally down-left direction.
        DownRight (int): Effect applied diagonally down-right direction.  
        FromBottom (int): Effect originating from the bottom.
        FromLeft (int): Effect originating from the left.
        FromRight (int): Effect originating from the right.
        FromTop (int): Effect originating from the top.
        Horizontal (int): Horizontal effect application.
        In (int): Effect moving inward.
        InHorizontal (int): Horizontal inward effect.
        InVertical (int): Vertical inward effect.
        Left (int):Effect applied to the left.
        Out (int): Effect moving outward.
        OutHorizontal (int): Horizontal outward effect.
        OutVertical (int):Vertical outward effect.
        Right (int): Effect applied to the right.
        Spokes1 (int): Spoke effect with 1 spoke.
        Spokes2 (int):Spoke effect with 2 spokes.
        Spokes3 (int): Spoke effect with 3 spokes.
        Spokes4 (int): Spoke effect with 4 spokes.
        Spokes8 (int): Spoke effect with 8 spokes.
        Up (int Effect applied upward.
        UpLeft (int): Effect applied diagonally up-left.
        UpRight (int): Effect applied diagonally up-right.
        Vertical (int): Vertical effect application.

    """
    none = 0
    Across = 1
    Down = 2
    DownLeft = 3
    DownRight = 4
    FromBottom = 5
    FromLeft = 6
    FromRight = 7
    FromTop = 8
    Horizontal = 9
    In = 10
    InHorizontal = 11
    InVertical = 12
    Left = 13
    Out = 14
    OutHorizontal = 15
    OutVertical = 16
    Right = 17
    Spokes1 = 18
    Spokes2 = 19
    Spokes3 = 20
    Spokes4 = 21
    Spokes8 = 22
    Up = 23
    UpLeft = 24
    UpRight = 25
    Vertical = 26

