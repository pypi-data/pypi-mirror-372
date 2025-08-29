from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class InvXTransition (  Transition) :
    """
    Represents an inverse X-axis transition effect between slides.
    Inherits from base Transition class.
    """
    @property
    def IsNotDefaultXDirection(self)->bool:
        """
        Indicates if non-default X-direction is used.
        Read/write.
        """
        GetDllLibPpt().InvXTransition_get_IsNotDefaultXDirection.argtypes=[c_void_p]
        GetDllLibPpt().InvXTransition_get_IsNotDefaultXDirection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().InvXTransition_get_IsNotDefaultXDirection,self.Ptr)
        return ret

    @IsNotDefaultXDirection.setter
    def IsNotDefaultXDirection(self, value:bool):
        GetDllLibPpt().InvXTransition_set_IsNotDefaultXDirection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().InvXTransition_set_IsNotDefaultXDirection,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Compares with another object.

        Args:
            obj: Object to compare with
        
        Returns:
            True if objects are equal
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().InvXTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().InvXTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().InvXTransition_Equals,self.Ptr, intPtrobj)
        return ret

