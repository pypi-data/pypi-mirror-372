from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IActiveSlide (  IActivePresentation) :
    """
    Represents an active slide component within a presentation.
    Provides access to the underlying slide instance.
    """
    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the associated slide object.
        Read-only ActiveSlide instance.
        """
        GetDllLibPpt().IActiveSlide_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IActiveSlide_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IActiveSlide_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


