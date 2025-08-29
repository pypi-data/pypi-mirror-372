from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SystemColorType(Enum):
    """
    Represents predefined system colors.
    
    Enumerates various system-defined color types used in UI elements.
    """
    none = -1
    ScrollBar = 0
    Background = 1
    ActiveCaption = 2
    InactiveCaption = 3
    Menu = 4
    Window = 5
    WindowFrame = 6
    MenuText = 7
    WindowText = 8
    CaptionText = 9
    ActiveBorder = 10
    InactiveBorder = 11
    AppWorkspace = 12
    Highlight = 13
    HighlightText = 14
    BtnFace = 15
    BtnShadow = 16
    GrayText = 17
    BtnText = 18
    InactiveCaptionText = 19
    BtnHighlight = 20
    ThreeDDkShadow = 21
    ThreeDLight = 22
    InfoText = 23
    InfoBk = 24
    HotLight = 25
    GradientActiveCaption = 26
    GradientInactiveCaption = 27
    MenuHighlight = 28
    MenuBar = 29

