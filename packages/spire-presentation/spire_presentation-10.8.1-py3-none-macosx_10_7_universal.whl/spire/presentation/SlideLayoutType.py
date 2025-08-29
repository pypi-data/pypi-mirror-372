from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideLayoutType(Enum):
    """
    Specifies the type of slide layout.

    Attributes:
        Custom: Custom layout (-1)
        Title: Title slide (0)
        Text: Text-only layout (1)
        TwoColumnText: Two-column text layout (2)
        Table: Table layout (3)
        TextAndChart: Text and chart side-by-side (4)
        ChartAndText: Chart and text side-by-side (5)
        Diagram: Diagram layout (6)
        Chart: Chart-only layout (7)
        TextAndClipArt: Text and clip art side-by-side (8)
        ClipArtAndText: Clip art and text side-by-side (9)
        TitleOnly: Title-only layout (10)
        Blank: Blank slide (11)
        TextAndObject: Text and object side-by-side (12)
        ObjectAndText: Object and text side-by-side (13)
        Object: Object-only layout (14)
        TitleAndObject: Title and object layout (15)
        TextAndMedia: Text and media side-by-side (16)
        MediaAndText: Media and text side-by-side (17)
        ObjectOverText: Object positioned over text (18)
        TextOverObject: Text positioned over object (19)
        TextAndTwoObjects: Text with two objects (20)
        TwoObjectsAndText: Two objects with text (21)
        TwoObjectsOverText: Two objects over text (22)
        FourObjects: Four objects arranged in quadrants (23)
        VerticalText: Vertical text layout (24)
        ClipArtAndVerticalText: Clip art with vertical text (25)
        VerticalTitleAndText: Vertical title and text (26)
        VerticalTitleAndTextOverChart: Vertical title/text over chart (27)
        TwoObjects: Two objects side-by-side (28)
        ObjectAndTwoObject: Object with two subordinate objects (29)
        TwoObjectsAndObject: Two objects with a primary object (30)
        SectionHeader: Section header layout (31)
        TwoTextAndTwoObjects: Two text sections with two objects (32)
        TitleObjectAndCaption: Title with object and caption (33)
        PictureAndCaption: Picture with caption layout (34)
    """
    Custom = -1
    Title = 0
    Text = 1
    TwoColumnText = 2
    Table = 3
    TextAndChart = 4
    ChartAndText = 5
    Diagram = 6
    Chart = 7
    TextAndClipArt = 8
    ClipArtAndText = 9
    TitleOnly = 10
    Blank = 11
    TextAndObject = 12
    ObjectAndText = 13
    Object = 14
    TitleAndObject = 15
    TextAndMedia = 16
    MediaAndText = 17
    ObjectOverText = 18
    TextOverObject = 19
    TextAndTwoObjects = 20
    TwoObjectsAndText = 21
    TwoObjectsOverText = 22
    FourObjects = 23
    VerticalText = 24
    ClipArtAndVerticalText = 25
    VerticalTitleAndText = 26
    VerticalTitleAndTextOverChart = 27
    TwoObjects = 28
    ObjectAndTwoObject = 29
    TwoObjectsAndObject = 30
    SectionHeader = 31
    TwoTextAndTwoObjects = 32
    TitleObjectAndCaption = 33
    PictureAndCaption = 34

