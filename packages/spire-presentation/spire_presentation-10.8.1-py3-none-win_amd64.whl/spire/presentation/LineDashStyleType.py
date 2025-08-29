from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineDashStyleType(Enum):
    """
    Specifies the pattern used for dashed lines.
    
    Attributes:
        none: No dash style (solid line)
        Solid: Continuous solid line
        Dot: Dotted pattern
        Dash: Standard dash pattern
        LargeDash: Longer dash pattern
        DashDot: Alternating dashes and dots
        LargeDashDot: Long dashes with dots
        LargeDashDotDot: Long dashes with double dots
        SystemDash: OS-default dash pattern
        SystemDot: OS-default dot pattern
        SystemDashDot: OS-default dash-dot pattern
        SystemDashDotDot: OS-default dash-dot-dot pattern
        Custom: User-defined pattern
    """
    none = -1
    Solid = 0
    Dot = 1
    Dash = 2
    LargeDash = 3
    DashDot = 4
    LargeDashDot = 5
    LargeDashDotDot = 6
    SystemDash = 7
    SystemDot = 8
    SystemDashDot = 9
    SystemDashDotDot = 10
    Custom = 11

