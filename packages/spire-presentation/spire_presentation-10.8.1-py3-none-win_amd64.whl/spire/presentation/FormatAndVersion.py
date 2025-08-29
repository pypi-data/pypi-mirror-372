from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FormatAndVersion(Enum):
    """
    Specifies file formats and versions for presentations.

    Enumerations:
        PPT: Legacy PowerPoint format
        Pptx2007: Office Open XML (2007)
        Pptx2010: Office Open XML (2010)
        Pptx2013: Office Open XML (2013)
        Pptx2016: Office Open XML (2016)
        PPS: PowerPoint Show (legacy)
        Ppsx2007: Show format (2007)
        Ppsx2010: Show format (2010)
        Ppsx2013: Show format (2013)
        Ppsx2016: Show format (2016)
        Odp: OpenDocument Presentation
        Uop: Universal Office Presentation
        Pot: PowerPoint Template (legacy)
        Potm2007: Macro-enabled Template (2007)
        Potm2010: Macro-enabled Template (2010)
        Potm2013: Macro-enabled Template (2013)
        Potm2016: Macro-enabled Template (2016)
        Potx2007: Template format (2007)
        Potx2010: Template format (2010)
        Potx2013: Template format (2013)
        Potx2016: Template format (2016)
        Pptm2007: Macro-enabled Presentation (2007)
        Pptm2010: Macro-enabled Presentation (2010)
        Pptm2013: Macro-enabled Presentation (2013)
        Pptm2016: Macro-enabled Presentation (2016)
        Ppsm2007: Macro-enabled Show (2007)
        Ppsm2010: Macro-enabled Show (2010)
        Ppsm2013: Macro-enabled Show (2013)
        Ppsm2016: Macro-enabled Show (2016)
    """
    PPT = 0
    Pptx2007 = 1
    Pptx2010 = 2
    Pptx2013 = 3
    Pptx2016 = 4
    PPS = 5
    Ppsx2007 = 6
    Ppsx2010 = 7
    Ppsx2013 = 8
    Ppsx2016 = 9
    Odp = 10
    Uop = 11
    Pot = 12
    Potm2007 = 13
    Potm2010 = 14
    Potm2013 = 15
    Potm2016 = 16
    Potx2007 = 17
    Potx2010 = 18
    Potx2013 = 19
    Potx2016 = 20
    Pptm2007 = 21
    Pptm2010 = 22
    Pptm2013 = 23
    Pptm2016 = 24
    Ppsm2007 = 25
    Ppsm2010 = 26
    Ppsm2013 = 27
    Ppsm2016 = 28

