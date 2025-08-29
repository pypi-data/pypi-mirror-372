from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationEffectType(Enum):
    """
    Represents predefined types of animation effects used in PowerPoint presentations.
    These effects define how objects enter, exit, or change during slide transitions.
    """
    Appear = 0
    """Object appears without any special effect."""
    
    ArcUp = 1
    """Object moves in an upward arc path."""
    
    Ascend = 2
    """Object rises upward from below."""
    
    Blast = 3
    """Object appears with an explosive effect."""
    
    Blinds = 4
    """Object appears through horizontal or vertical blinds effect."""
    
    Blink = 5
    """Object blinks briefly during transition."""
    
    BoldFlash = 6
    """Text flashes briefly with bold emphasis."""
    
    BoldReveal = 7
    """Text is revealed with bold emphasis."""
    
    Boomerang = 8
    """Object moves out and returns like a boomerang."""
    
    Bounce = 9
    """Object bounces into position."""
    
    Box = 10
    """Object appears within a box shape."""
    
    BrushOnColor = 11
    """Color is brushed onto the object."""
    
    BrushOnUnderline = 12
    """Underline is brushed onto text."""
    
    CenterRevolve = 13
    """Object revolves around its center point."""
    
    ChangeFillColor = 14
    """Changes the fill color of an object."""
    
    ChangeFont = 15
    """Changes the font of text."""
    
    ChangeFontColor = 16
    """Changes the color of text."""
    
    ChangeFontSize = 17
    """Changes the size of text."""
    
    ChangeFontStyle = 18
    """Changes the style of text (bold, italic, etc.)."""
    
    ChangeLineColor = 19
    """Changes the color of lines in shapes."""
    
    Checkerboard = 20
    """Object appears in a checkerboard pattern."""
    
    Circle = 21
    """Object appears within a circle shape."""
    
    ColorBlend = 22
    """Colors blend during transition."""
    
    ColorReveal = 23
    """Object is revealed through color changes."""
    
    ColorWave = 24
    """Colors wave across the object."""
    
    ComplementaryColor = 25
    """Changes to a complementary color scheme."""
    
    ComplementaryColor2 = 26
    """Alternative complementary color effect."""
    
    Compress = 27
    """Object appears compressed then expands."""
    
    ContrastingColor = 28
    """Changes to a contrasting color scheme."""
    
    Crawl = 29
    """Text crawls across the screen."""
    
    Credits = 30
    """Text scrolls like movie credits."""
    
    Darken = 31
    """Object darkens during transition."""
    
    Desaturate = 32
    """Colors become desaturated."""
    
    Descend = 33
    """Object descends from above."""
    
    Diamond = 34
    """Object appears within a diamond shape."""
    
    Dissolve = 35
    """Object dissolves into view."""
    
    EaseIn = 36
    """Object eases into position smoothly."""
    
    Expand = 37
    """Object expands from a point."""
    
    Fade = 38
    """Object fades into view."""
    
    FadedSwivel = 39
    """Object swivels while fading."""
    
    FadedZoom = 40
    """Object zooms while fading."""
    
    FlashBulb = 41
    """Flash bulb effect like a camera."""
    
    FlashOnce = 42
    """Object flashes once briefly."""
    
    Flicker = 43
    """Object flickers during transition."""
    
    Flip = 44
    """Object flips like a card."""
    
    Float = 45
    """Object floats into position."""
    
    Fly = 46
    """Object flies in from off-screen."""
    
    Fold = 47
    """Object folds like paper."""
    
    Glide = 48
    """Object glides smoothly into position."""
    
    GrowAndTurn = 49
    """Object grows while turning."""
    
    GrowShrink = 50
    """Object grows then shrinks."""
    
    GrowWithColor = 51
    """Object grows while changing color."""
    
    Lighten = 52
    """Object lightens during transition."""
    
    LightSpeed = 53
    """Object moves at light speed."""
    
    MediaPause = 54
    """Animation effect for pausing media."""
    
    MediaPlay = 55
    """Animation effect for playing media."""
    
    MediaStop = 56
    """Animation effect for stopping media."""
    
    Path4PointStar = 57
    """Object moves along a 4-point star path."""
    
    Path5PointStar = 58
    """Object moves along a 5-point star path."""
    
    Path6PointStar = 59
    """Object moves along a 6-point star path."""
    
    Path8PointStar = 60
    """Object moves along an 8-point star path."""
    
    PathArcDown = 61
    """Object moves along a downward arc path."""
    
    PathArcLeft = 62
    """Object moves along a leftward arc path."""
    
    PathArcRight = 63
    """Object moves along a rightward arc path."""
    
    PathArcUp = 64
    """Object moves along an upward arc path."""
    
    PathBean = 65
    """Object moves along a bean-shaped path."""
    
    PathBounceLeft = 66
    """Object bounces along a leftward path."""
    
    PathBounceRight = 67
    """Object bounces along a rightward path."""
    
    PathBuzzsaw = 68
    """Object moves along a buzzsaw-shaped path."""
    
    PathCircle = 69
    """Object moves along a circular path."""
    
    PathCrescentMoon = 70
    """Object moves along a crescent moon path."""
    
    PathCurvedSquare = 71
    """Object moves along a curved square path."""
    
    PathCurvedX = 72
    """Object moves along a curved X-shaped path."""
    
    PathCurvyLeft = 73
    """Object moves along a curvy leftward path."""
    
    PathCurvyRight = 74
    """Object moves along a curvy rightward path."""
    
    PathCurvyStar = 75
    """Object moves along a curvy star path."""
    
    PathDecayingWave = 76
    """Object moves along a decaying wave path."""
    
    PathDiagonalDownRight = 77
    """Object moves diagonally down to the right."""
    
    PathDiagonalUpRight = 78
    """Object moves diagonally up to the right."""
    
    PathDiamond = 79
    """Object moves along a diamond-shaped path."""
    
    PathDown = 80
    """Object moves downward."""
    
    PathEqualTriangle = 81
    """Object moves along an equilateral triangle path."""
    
    PathFigure8Four = 82
    """Object moves along a figure-8 path with four loops."""
    
    PathFootball = 83
    """Object moves along a football-shaped path."""
    
    PathFunnel = 84
    """Object moves along a funnel-shaped path."""
    
    PathHeart = 85
    """Object moves along a heart-shaped path."""
    
    PathHeartbeat = 86
    """Object moves along a heartbeat monitor path."""
    
    PathHexagon = 87
    """Object moves along a hexagonal path."""
    
    PathHorizontalFigure8 = 88
    """Object moves along a horizontal figure-8 path."""
    
    PathInvertedSquare = 89
    """Object moves along an inverted square path."""
    
    PathInvertedTriangle = 90
    """Object moves along an inverted triangle path."""
    
    PathLeft = 91
    """Object moves leftward."""
    
    PathLoopdeLoop = 92
    """Object moves along a looping path."""
    
    PathNeutron = 93
    """Object moves along a neutron-like path."""
    
    PathOctagon = 94
    """Object moves along an octagonal path."""
    
    PathParallelogram = 95
    """Object moves along a parallelogram path."""
    
    PathPeanut = 96
    """Object moves along a peanut-shaped path."""
    
    PathPentagon = 97
    """Object moves along a pentagonal path."""
    
    PathPlus = 98
    """Object moves along a plus-shaped path."""
    
    PathPointyStar = 99
    """Object moves along a pointy star path."""
    
    PathRight = 100
    """Object moves rightward."""
    
    PathRightTriangle = 101
    """Object moves along a right triangle path."""
    
    PathSCurve1 = 102
    """Object moves along an S-curve path (type 1)."""
    
    PathSCurve2 = 103
    """Object moves along an S-curve path (type 2)."""
    
    PathSineWave = 104
    """Object moves along a sine wave path."""
    
    PathSpiralLeft = 105
    """Object spirals leftward."""
    
    PathSpiralRight = 106
    """Object spirals rightward."""
    
    PathSpring = 107
    """Object moves along a spring-like path."""
    
    PathSquare = 108
    """Object moves along a square path."""
    
    PathStairsDown = 109
    """Object moves down like stairs."""
    
    PathSwoosh = 110
    """Object moves with a swooshing motion."""
    
    PathTeardrop = 111
    """Object moves along a teardrop-shaped path."""
    
    PathTrapezoid = 112
    """Object moves along a trapezoidal path."""
    
    PathTurnDown = 113
    """Object turns downward."""
    
    PathTurnRight = 114
    """Object turns rightward."""
    
    PathTurnUp = 115
    """Object turns upward."""
    
    PathTurnUpRight = 116
    """Object turns up and to the right."""
    
    PathUp = 117
    """Object moves upward."""
    
    PathUser = 118
    """Custom user-defined motion path."""
    
    PathVerticalFigure8 = 119
    """Object moves along a vertical figure-8 path."""
    
    PathWave = 120
    """Object moves along a wave path."""
    
    PathZigzag = 121
    """Object moves along a zigzag path."""
    
    Peek = 122
    """Object peeks in from off-screen."""
    
    Pinwheel = 123
    """Object spins like a pinwheel."""
    
    Plus = 124
    """Object appears with a plus sign effect."""
    
    RandomBars = 125
    """Object appears with random bars effect."""
    
    RandomEffects = 126
    """Random combination of animation effects."""
    
    RiseUp = 127
    """Object rises up from below."""
    
    Shimmer = 128
    """Object shimmers during transition."""
    
    Sling = 129
    """Object slings into position."""
    
    Spin = 130
    """Object spins around its center."""
    
    Spinner = 131
    """Object spins like a spinner."""
    
    Spiral = 132
    """Object appears in a spiral pattern."""
    
    Split = 133
    """Object splits apart."""
    
    Stretch = 134
    """Object stretches during transition."""
    
    Strips = 135
    """Object appears in strips."""
    
    StyleEmphasis = 136
    """Emphasizes text with style changes."""
    
    Swish = 137
    """Object moves with a swishing sound effect."""
    
    Swivel = 138
    """Object swivels during transition."""
    
    Teeter = 139
    """Object teeters back and forth."""
    
    Thread = 140
    """Text appears threaded together."""
    
    Transparency = 141
    """Object becomes transparent."""
    
    Unfold = 142
    """Object unfolds into view."""
    
    VerticalGrow = 143
    """Object grows vertically."""
    
    Wave = 144
    """Object waves during transition."""
    
    Wedge = 145
    """Object appears with a wedge effect."""
    
    Wheel = 146
    """Object appears with a wheel effect."""
    
    Whip = 147
    """Object whips into position."""
    
    Wipe = 148
    """Object wipes into view."""
    
    Magnify = 149
    """Object magnifies during transition."""
    
    Zoom = 150
    """Object zooms into view."""

