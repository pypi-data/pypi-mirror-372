from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FileFormat(Enum):
    """
    Specifies presentation file format types.
    
    Enumeration Members:
        Auto: Automatic format detection
        PPT: Microsoft PowerPoint 97-2003 format
        Pptx2007: PowerPoint 2007 format
        Pptx2010: PowerPoint 2010 format
        Pptx2013: PowerPoint 2013 format
        Pptx2016: PowerPoint 2016 format
        Pptx2019: PowerPoint 2019 format
        Pptm: Macro-enabled presentation
        Ppsx2007 - Ppsx2019: Slide show formats
        PPS: PowerPoint 97-2003 slide show
        ODP: OpenDocument Presentation
        Html: HTML format
        XPS: XML Paper Specification
        PCL: Printer Command Language
        PS: PostScript
        OFD: Open Fixed-layout Document
        PDF: Portable Document Format
        Potx: PowerPoint template
        Dps: Kingsoft Presentation
        Dpt: Kingsoft Template
    """
    Auto = 0
    PPT = 1
    Pptx2007 = 2
    Pptx2010 = 3
    Pptx2013 = 4
    Pptx2016 = 5
    Pptx2019 = 6
    Pptm = 7
    Ppsx2007 = 8
    Ppsx2010 = 9
    Ppsx2013 = 10
    Ppsx2016 = 11
    Ppsx2019 = 12
    PPS = 13
    ODP = 14
    #UOP = 15
    Html = 16
    #Tiff = 17
    XPS = 18
    PCL = 19
    PS = 20
    OFD = 21
    PDF = 22
    Potx = 23
    Dps = 24
    Dpt = 25
    #Bin = 26

