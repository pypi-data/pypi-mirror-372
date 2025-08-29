from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SmartArtColorType(Enum):
    """
    Defines color schemes for SmartArt diagrams in presentations.
    """
    Dark1Outline = 0
    Dark2Outline = 1
    DarkFill = 2
    ColorfulAccentColors = 3
    ColorfulAccentColors2to3 = 4
    ColorfulAccentColors3to4 = 5
    ColorfulAccentColors4to5 = 6
    ColorfulAccentColors5to6 = 7
    ColoredOutlineAccent1 = 8
    ColoredFillAccent1 = 9
    GradientRangeAccent1 = 10
    GradientLoopAccent1 = 11
    TransparentGradientRangeAccent1 = 12
    ColoredOutlineAccent2 = 13
    ColoredFillAccent2 = 14
    GradientRangeAccent2 = 15
    GradientLoopAccent2 = 16
    TransparentGradientRangeAccent2 = 17
    ColoredOutlineAccent3 = 18
    ColoredFillAccent3 = 19
    GradientRangeAccent3 = 20
    GradientLoopAccent3 = 21
    TransparentGradientRangeAccent3 = 22
    ColoredOutlineAccent4 = 23
    ColoredFillAccent4 = 24
    GradientRangeAccent4 = 25
    GradientLoopAccent4 = 26
    TransparentGradientRangeAccent4 = 27
    ColoredOutlineAccent5 = 28
    ColoredFillAccent5 = 29
    GradientRangeAccent5 = 30
    GradientLoopAccent5 = 31
    TransparentGradientRangeAccent5 = 32
    ColoredOutlineAccent6 = 33
    ColoredFillAccent6 = 34
    GradientRangeAccent6 = 35
    GradientLoopAccent6 = 36
    TransparentGradientRangeAccent6 = 37

