from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideSizeType(Enum):
    """
    Enumerates different standard slide size presets used in presentations.
    
    Attributes:
        none: No predefined size
        Screen4x3: Standard screen aspect ratio (4:3)
        Letter: US Letter paper size (8.5 x 11 inches)
        A4: ISO A4 paper size (210 x 297 mm)
        Film35mm: Standard 35mm film frame size
        Overhead: Overhead projector slide size
        Banner: Banner/poster format
        Custom: Custom-sized slides
        Ledger: Ledger/tabloid paper size (11 x 17 inches)
        A3: ISO A3 paper size (297 x 420 mm)
        B4ISO: ISO B4 paper size (250 x 353 mm)
        B5ISO: ISO B5 paper size (176 x 250 mm)
        B4JIS: JIS B4 paper size (257 x 364 mm)
        B5JIS: JIS B5 paper size (182 x 257 mm)
        HagakiCard: Japanese postcard size (100 x 148 mm)
        Screen16x9: Widescreen aspect ratio (16:9)
        Screen16x10: Alternate widescreen aspect ratio (16:10)
    """
    none = -1
    Screen4x3 = 0
    Letter = 1
    A4 = 2
    Film35mm = 3
    Overhead = 4
    Banner = 5
    Custom = 6
    Ledger = 7
    A3 = 8
    B4ISO = 9
    B5ISO = 10
    B4JIS = 11
    B5JIS = 12
    HagakiCard = 13
    Screen16x9 = 14
    Screen16x10 = 15

