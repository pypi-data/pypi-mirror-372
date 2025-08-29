from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextShapeType(Enum):
    """
    Enum representing text wrapping shapes.
    
    Attributes:
        UnDefined: Undefined shape
        none: No wrapping shape
        Plain: Plain shape
        Stop: Stop shape
        Triangle: Triangle shape
        TriangleInverted: Inverted triangle shape
        Chevron: Chevron shape
        ChevronInverted: Inverted chevron shape
        RingInside: Inside ring shape
        RingOutside: Outside ring shape
        ArchUp: Upward arch shape
        ArchDown: Downward arch shape
        Circle: Circle shape
        Button: Button shape
        ArchUpPour: Upward arch pour shape
        ArchDownPour: Downward arch pour shape
        CirclePour: Circle pour shape
        ButtonPour: Button pour shape
        CurveUp: Upward curve shape
        CurveDown: Downward curve shape
        CanUp: Upward can shape
        CanDown: Downward can shape
        Wave1: Wave type 1 shape
        Wave2: Wave type 2 shape
        DoubleWave1: Double wave type 1 shape
        Wave4: Wave type 4 shape
        Inflate: Inflate shape
        Deflate: Deflate shape
        InflateBottom: Bottom inflate shape
        DeflateBottom: Bottom deflate shape
        InflateTop: Top inflate shape
        DeflateTop: Top deflate shape
        DeflateInflate: Deflate-inflate shape
        DeflateInflateDeflate: Deflate-inflate-deflate shape
        FadeRight: Right fade shape
        FadeLeft: Left fade shape
        FadeUp: Upward fade shape
        FadeDown: Downward fade shape
        SlantUp: Upward slant shape
        SlantDown: Downward slant shape
        CascadeUp: Upward cascade shape
        CascadeDown: Downward cascade shape
        Custom: Custom shape
    """
    UnDefined = -1
    none = 0
    Plain = 1
    Stop = 2
    Triangle = 3
    TriangleInverted = 4
    Chevron = 5
    ChevronInverted = 6
    RingInside = 7
    RingOutside = 8
    ArchUp = 9
    ArchDown = 10
    Circle = 11
    Button = 12
    ArchUpPour = 13
    ArchDownPour = 14
    CirclePour = 15
    ButtonPour = 16
    CurveUp = 17
    CurveDown = 18
    CanUp = 19
    CanDown = 20
    Wave1 = 21
    Wave2 = 22
    DoubleWave1 = 23
    Wave4 = 24
    Inflate = 25
    Deflate = 26
    InflateBottom = 27
    DeflateBottom = 28
    InflateTop = 29
    DeflateTop = 30
    DeflateInflate = 31
    DeflateInflateDeflate = 32
    FadeRight = 33
    FadeLeft = 34
    FadeUp = 35
    FadeDown = 36
    SlantUp = 37
    SlantDown = 38
    CascadeUp = 39
    CascadeDown = 40
    Custom = 41

