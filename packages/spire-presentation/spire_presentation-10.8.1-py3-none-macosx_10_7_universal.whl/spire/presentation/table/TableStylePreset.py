from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TableStylePreset(Enum):
    """
    Specifies built-in table styles for presentation tables.
    """
    Custom = -1
    none = 0
    MediumStyle2Accent1 = 1
    MediumStyle2 = 2
    NoStyleNoGrid = 3
    ThemedStyle1Accent1 = 4
    ThemedStyle1Accent2 = 5
    ThemedStyle1Accent3 = 6
    ThemedStyle1Accent4 = 7
    ThemedStyle1Accent5 = 8
    ThemedStyle1Accent6 = 9
    NoStyleTableGrid = 10
    ThemedStyle2Accent1 = 11
    ThemedStyle2Accent2 = 12
    ThemedStyle2Accent3 = 13
    ThemedStyle2Accent4 = 14
    ThemedStyle2Accent5 = 15
    ThemedStyle2Accent6 = 16
    LightStyle1 = 17
    LightStyle1Accent1 = 18
    LightStyle1Accent2 = 19
    LightStyle1Accent3 = 20
    LightStyle1Accent4 = 21
    LightStyle2Accent5 = 22
    LightStyle1Accent6 = 23
    LightStyle2 = 24
    LightStyle2Accent1 = 25
    LightStyle2Accent2 = 26
    LightStyle2Accent3 = 27
    MediumStyle2Accent3 = 28
    MediumStyle2Accent4 = 29
    MediumStyle2Accent5 = 30
    LightStyle2Accent6 = 31
    LightStyle2Accent4 = 32
    LightStyle3 = 33
    LightStyle3Accent1 = 34
    MediumStyle2Accent2 = 35
    LightStyle3Accent2 = 36
    LightStyle3Accent3 = 37
    LightStyle3Accent4 = 38
    LightStyle3Accent5 = 39
    LightStyle3Accent6 = 40
    MediumStyle1 = 41
    MediumStyle1Accent1 = 42
    MediumStyle1Accent2 = 43
    MediumStyle1Accent3 = 44
    MediumStyle1Accent4 = 45
    MediumStyle1Accent5 = 46
    MediumStyle1Accent6 = 47
    MediumStyle2Accent6 = 48
    MediumStyle3 = 49
    MediumStyle3Accent1 = 50
    MediumStyle3Accent2 = 51
    MediumStyle3Accent3 = 52
    MediumStyle3Accent4 = 53
    MediumStyle3Accent5 = 54
    MediumStyle3Accent6 = 55
    MediumStyle4 = 56
    MediumStyle4Accent1 = 57
    MediumStyle4Accent2 = 58
    MediumStyle4Accent3 = 59
    MediumStyle4Accent4 = 60
    MediumStyle4Accent5 = 61
    MediumStyle4Accent6 = 62
    DarkStyle1 = 63
    DarkStyle1Accent1 = 64
    DarkStyle1Accent2 = 65
    DarkStyle1Accent3 = 66
    DarkStyle1Accent4 = 67
    DarkStyle1Accent5 = 68
    DarkStyle1Accent6 = 69
    DarkStyle2 = 70
    DarkStyle2Accent1Accent2 = 71
    DarkStyle2Accent3Accent4 = 72
    DarkStyle2Accent5Accent6 = 73

