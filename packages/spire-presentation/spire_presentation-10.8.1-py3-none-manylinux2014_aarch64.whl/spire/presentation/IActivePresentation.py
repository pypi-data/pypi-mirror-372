from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IActivePresentation (SpireObject) :
    """
    Base interface for components that belong to a presentation.

    """
    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent Presentation object that contains this component.

        Returns:
            Presentation: The parent presentation instance
        """
        GetDllLibPpt().IActivePresentation_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IActivePresentation_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IActivePresentation_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


