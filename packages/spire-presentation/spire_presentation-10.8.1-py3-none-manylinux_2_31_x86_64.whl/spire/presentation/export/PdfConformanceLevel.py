from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PdfConformanceLevel(Enum):
    """
    Specifies the conformance level for PDF documents.
    
    Attributes:
        none: No specific conformance level.
        Pdf_A1B: PDF/A-1b conformance level.
        Pdf_X1A2001: PDF/X-1a:2001 conformance level.
        Pdf_A1A: PDF/A-1a conformance level.
        Pdf_A2A: PDF/A-2a conformance level.
        Pdf_A2B: PDF/A-2b conformance level.
        Pdf_A3A: PDF/A-3a conformance level.
        Pdf_A3B: PDF/A-3b conformance level.
    """
    none = -1
    Pdf_A1B = 0
    Pdf_X1A2001 = 1
    Pdf_A1A = 2
    Pdf_A2A = 3
    Pdf_A2B = 4
    Pdf_A3A = 5
    Pdf_A3B = 6