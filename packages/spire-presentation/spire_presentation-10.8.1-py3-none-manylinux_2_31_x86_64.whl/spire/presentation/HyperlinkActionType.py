from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class HyperlinkActionType(Enum):
    """
    Defines types of actions that can be triggered by hyperlinks in presentations.

    Attributes:
        none: No action defined (placeholder state)
        NoAction: Hyperlink exists but performs no action
        Hyperlink: Standard web URL or document link
        GotoFirstSlide: Navigates to the first slide in presentation
        GotoPrevSlide: Navigates to previous slide
        GotoNextSlide: Navigates to next slide
        GotoLastSlide: Navigates to last slide in presentation
        GotoEndShow: Ends the current slide show
        GotoLastViewedSlide: Returns to last viewed slide
        GotoSlide: Jumps to specific slide by index
        StartCustomSlideShow: Starts custom slide show sequence
        OpenFile: Opens external file
        OpenPresentation: Opens another presentation file
        StartStopMedia: Controls media playback
        StartMacro: Executes macro
        StartProgram: Launches external application
    """
    none = -1
    NoAction = 0
    Hyperlink = 1
    GotoFirstSlide = 2
    GotoPrevSlide = 3
    GotoNextSlide = 4
    GotoLastSlide = 5
    GotoEndShow = 6
    GotoLastViewedSlide = 7
    GotoSlide = 8
    StartCustomSlideShow = 9
    OpenFile = 10
    OpenPresentation = 11
    StartStopMedia = 12
    StartMacro = 13
    StartProgram = 14

