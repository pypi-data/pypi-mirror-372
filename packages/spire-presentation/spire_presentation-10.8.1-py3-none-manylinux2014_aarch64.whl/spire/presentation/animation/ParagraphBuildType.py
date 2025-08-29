from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ParagraphBuildType(Enum):
    """
    Specifies how text is displayed during animation sequences.
    
    Attributes:
        Whole: Display the entire paragraph at once
        AllAtOnce: Display all paragraphs simultaneously
        Paragraphs1: Build by individual paragraphs (level 1)
        Paragraphs2: Build by individual paragraphs (level 2)
        Paragraphs3: Build by individual paragraphs (level 3)
        Paragraphs4: Build by individual paragraphs (level 4)
        Paragraphs5: Build by individual paragraphs (level 5)
        cust: Custom build behavior
    """
    Whole = 0
    AllAtOnce = 1
    Paragraphs1 = 2
    Paragraphs2 = 3
    Paragraphs3 = 4
    Paragraphs4 = 5
    Paragraphs5 = 6
    cust = 7

