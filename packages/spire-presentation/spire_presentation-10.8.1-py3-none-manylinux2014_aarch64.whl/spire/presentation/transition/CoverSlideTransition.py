from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CoverSlideTransition (  Transition) :
    """
    Represents an eight-direction slide transition effect (cover style).
    
    This transition effect slides the new slide over the current slide from a specified direction.
    """
    @property

    def Direction(self)->'TransitionEightDirection':
        """
        Gets or sets the direction of the cover transition.
        
        Returns:
            The current transition direction.
        """
        GetDllLibPpt().CoverSlideTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().CoverSlideTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CoverSlideTransition_get_Direction,self.Ptr)
        objwraped = TransitionEightDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionEightDirection'):
        """
        Sets the direction of the cover transition.
        
        Args:
            value: The new transition direction.
        """
        GetDllLibPpt().CoverSlideTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().CoverSlideTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current object is equal to another object.
        
        Args:
            obj: The object to compare with.
        
        Returns:
            True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().CoverSlideTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CoverSlideTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CoverSlideTransition_Equals,self.Ptr, intPtrobj)
        return ret

