from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OptionalBlackTransition (  Transition) :
    """
    Represents an optional black slide transition effect between slides.
    This transition effect can optionally start from a black screen before transitioning to the new slide.
    
    Attributes:
        FromBlack (bool): Controls whether the transition starts from a black screen.
    """
    @property
    def FromBlack(self)->bool:
        """
        Determines if the transition starts from a black screen.
        
        Returns:
            bool: True if the transition starts from a black screen; otherwise, False.
        """
        GetDllLibPpt().OptionalBlackTransition_get_FromBlack.argtypes=[c_void_p]
        GetDllLibPpt().OptionalBlackTransition_get_FromBlack.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OptionalBlackTransition_get_FromBlack,self.Ptr)
        return ret

    @FromBlack.setter
    def FromBlack(self, value:bool):
        GetDllLibPpt().OptionalBlackTransition_set_FromBlack.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().OptionalBlackTransition_set_FromBlack,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current transition object.
        
        Args:
            obj (SpireObject): The object to compare with the current object.
        
        Returns:
            bool: True if the specified object is equal to the current object; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().OptionalBlackTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().OptionalBlackTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OptionalBlackTransition_Equals,self.Ptr, intPtrobj)
        return ret

