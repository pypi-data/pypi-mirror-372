from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PlaceholderType(Enum):
    """
    Specifies the type of content a placeholder can hold.

    Attributes:
        Title: Title placeholder
        Body: Body text placeholder
        CenteredTitle: Centered title placeholder
        Subtitle: Subtitle placeholder
        DateAndTime: Date and time placeholder
        SlideNumber: Slide number placeholder
        Footer: Footer placeholder
        Header: Header placeholder
        Object: Generic object placeholder
        Chart: Chart placeholder
        Table: Table placeholder
        ClipArt: Clip art placeholder
        Diagram: Diagram placeholder
        Media: Media placeholder
        SlideImage: Slide image placeholder
        Picture: Picture placeholder
        none: No specific placeholder type
    """
    Title = 0
    Body = 1
    CenteredTitle = 2
    Subtitle = 3
    DateAndTime = 4
    SlideNumber = 5
    Footer = 6
    Header = 7
    Object = 8
    Chart = 9
    Table = 10
    ClipArt = 11
    Diagram = 12
    Media = 13
    SlideImage = 14
    Picture = 15
    none = 16

