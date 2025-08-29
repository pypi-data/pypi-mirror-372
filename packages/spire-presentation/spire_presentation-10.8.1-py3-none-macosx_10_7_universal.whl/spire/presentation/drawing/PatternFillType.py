from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PatternFillType(Enum):
    """
    Represents different pattern styles for fills.

    Enumeration Members:
        UnDefined: Undefined pattern style
        none: No pattern
        Percent05: 5% pattern density
        Percent10: 10% pattern density
        Percent20: 20% pattern density
        Percent25: 25% pattern density
        Percent30: 30% pattern density
        Percent40: 40% pattern density
        Percent50: 50% pattern density
        Percent60: 60% pattern density
        Percent70: 70% pattern density
        Percent75: 75% pattern density
        Percent80: 80% pattern density
        Percent90: 90% pattern density
        DarkHorizontal: Dark horizontal lines pattern
        DarkVertical: Dark vertical lines pattern
        DarkDownwardDiagonal: Dark downward diagonal lines pattern
        DarkUpwardDiagonal: Dark upward diagonal lines pattern
        SmallCheckerBoard: Small checkerboard pattern
        Trellis: Trellis pattern
        LightHorizontal: Light horizontal lines pattern
        LightVertical: Light vertical lines pattern
        LightDownwardDiagonal: Light downward diagonal lines pattern
        LightUpwardDiagonal: Light upward diagonal lines pattern
        SmallGrid: Small grid pattern
        DottedDiamond: Dotted diamond pattern
        WideDownwardDiagonal: Wide downward diagonal lines pattern
        WideUpwardDiagonal: Wide upward diagonal lines pattern
        DashedUpwardDiagonal: Dashed upward diagonal lines pattern
        DashedDownwardDiagonal: Dashed downward diagonal lines pattern
        NarrowVertical: Narrow vertical lines pattern
        NarrowHorizontal: Narrow horizontal lines pattern
        DashedVertical: Dashed vertical lines pattern
        DashedHorizontal: Dashed horizontal lines pattern
        LargeConfetti: Large confetti pattern
        LargeGrid: Large grid pattern
        HorizontalBrick: Horizontal brick pattern
        LargeCheckerBoard: Large checkerboard pattern
        SmallConfetti: Small confetti pattern
        Zigzag: Zigzag pattern
        SolidDiamond: Solid diamond pattern
        DiagonalBrick: Diagonal brick pattern
        OutlinedDiamond: Outlined diamond pattern
        Plaid: Plaid pattern
        Sphere: Sphere pattern
        Weave: Weave pattern
        DottedGrid: Dotted grid pattern
        Divot: Divot pattern
        Shingle: Shingle pattern
        Wave: Wave pattern
        Horizontal: Horizontal lines pattern
        Vertical: Vertical lines pattern
        Cross: Cross pattern
        DownwardDiagonal: Downward diagonal lines pattern
        UpwardDiagonal: Upward diagonal lines pattern
        DiagonalCross: Diagonal cross pattern
    """
    UnDefined = -1
    none = 0
    Percent05 = 1
    Percent10 = 2
    Percent20 = 3
    Percent25 = 4
    Percent30 = 5
    Percent40 = 6
    Percent50 = 7
    Percent60 = 8
    Percent70 = 9
    Percent75 = 10
    Percent80 = 11
    Percent90 = 12
    DarkHorizontal = 13
    DarkVertical = 14
    DarkDownwardDiagonal = 15
    DarkUpwardDiagonal = 16
    SmallCheckerBoard = 17
    Trellis = 18
    LightHorizontal = 19
    LightVertical = 20
    LightDownwardDiagonal = 21
    LightUpwardDiagonal = 22
    SmallGrid = 23
    DottedDiamond = 24
    WideDownwardDiagonal = 25
    WideUpwardDiagonal = 26
    DashedUpwardDiagonal = 27
    DashedDownwardDiagonal = 28
    NarrowVertical = 29
    NarrowHorizontal = 30
    DashedVertical = 31
    DashedHorizontal = 32
    LargeConfetti = 33
    LargeGrid = 34
    HorizontalBrick = 35
    LargeCheckerBoard = 36
    SmallConfetti = 37
    Zigzag = 38
    SolidDiamond = 39
    DiagonalBrick = 40
    OutlinedDiamond = 41
    Plaid = 42
    Sphere = 43
    Weave = 44
    DottedGrid = 45
    Divot = 46
    Shingle = 47
    Wave = 48
    Horizontal = 49
    Vertical = 50
    Cross = 51
    DownwardDiagonal = 52
    UpwardDiagonal = 53
    DiagonalCross = 54

