from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationEffectSubtype(Enum):
    """
    Represents subtypes of animation effects in PowerPoint presentations.
    These subtypes define variations and specific behaviors for animation effects.

    """
    none = 0
    """No specific subtype defined for the animation effect."""
    
    Across = 1
    """Animation moves across the screen horizontally."""
    
    Bottom = 2
    """Animation enters or exits from the bottom of the screen."""
    
    BottomLeft = 3
    """Animation enters or exits from the bottom-left corner of the screen."""
    
    BottomRight = 4
    """Animation enters or exits from the bottom-right corner of the screen."""
    
    Center = 5
    """Animation originates from or converges to the center of the screen."""
    
    Clockwise = 6
    """Animation rotates in a clockwise direction."""
    
    CounterClockwise = 7
    """Animation rotates in a counter-clockwise direction."""
    
    GradualAndCycleClockwise = 8
    """Animation gradually cycles in a clockwise direction."""
    
    GradualAndCycleCounterClockwise = 9
    """Animation gradually cycles in a counter-clockwise direction."""
    
    Down = 10
    """Animation moves downward on the screen."""
    
    DownLeft = 11
    """Animation moves diagonally down to the left."""
    
    DownRight = 12
    """Animation moves diagonally down to the right."""
    
    FontAllCaps = 13
    """Animation effect specific to changing text to all capital letters."""
    
    FontBold = 14
    """Animation effect specific to applying bold formatting to text."""
    
    FontItalic = 15
    """Animation effect specific to applying italic formatting to text."""
    
    FontShadow = 16
    """Animation effect specific to applying shadow effect to text."""
    
    FontStrikethrough = 17
    """Animation effect specific to applying strikethrough formatting to text."""
    
    FontUnderline = 18
    """Animation effect specific to applying underline formatting to text."""
    
    Gradual = 19
    """Animation occurs gradually over time."""
    
    Horizontal = 20
    """Animation moves horizontally across the screen."""
    
    HorizontalIn = 21
    """Animation enters horizontally from the edges toward the center."""
    
    HorizontalOut = 22
    """Animation exits horizontally from the center toward the edges."""
    
    In = 23
    """Generic entrance animation effect."""
    
    InBottom = 24
    """Animation enters from the bottom of the screen."""
    
    InCenter = 25
    """Animation enters from the center of the screen."""
    
    InSlightly = 26
    """Animation enters with a subtle, slight motion."""
    
    Instant = 27
    """Animation occurs instantly without any transition."""
    
    Left = 28
    """Animation moves to the left side of the screen."""
    
    OrdinalMask = 29
    """Special mask effect for ordinal animations."""
    
    Out = 30
    """Generic exit animation effect."""
    
    OutBottom = 31
    """Animation exits toward the bottom of the screen."""
    
    OutCenter = 32
    """Animation exits from the center of the screen."""
    
    OutSlightly = 33
    """Animation exits with a subtle, slight motion."""
    
    Right = 34
    """Animation moves to the right side of the screen."""
    
    Slightly = 35
    """Animation occurs with subtle, slight motion."""
    
    Top = 36
    """Animation enters or exits from the top of the screen."""
    
    TopLeft = 37
    """Animation enters or exits from the top-left corner of the screen."""
    
    TopRight = 38
    """Animation enters or exits from the top-right corner of the screen."""
    
    Up = 39
    """Animation moves upward on the screen."""
    
    UpLeft = 40
    """Animation moves diagonally up to the left."""
    
    UpRight = 41
    """Animation moves diagonally up to the right."""
    
    Vertical = 42
    """Animation moves vertically on the screen."""
    
    VerticalIn = 43
    """Animation enters vertically from the top or bottom toward the center."""
    
    VerticalOut = 44
    """Animation exits vertically from the center toward the top or bottom."""
    
    Wheel1 = 45
    """Wheel animation effect with 1 spoke."""
    
    Wheel2 = 46
    """Wheel animation effect with 2 spokes."""
    
    Wheel3 = 47
    """Wheel animation effect with 3 spokes."""
    
    Wheel4 = 48
    """Wheel animation effect with 4 spokes."""
    
    Wheel8 = 49
    """Wheel animation effect with 8 spokes."""

