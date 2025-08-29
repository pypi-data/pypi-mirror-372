from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ZoomSlideTransition (  Transition) :
    """Represents a zoom slide transition effect."""
    @property

    def Direction(self)->'TransitionInOutDirection':
        """
        Gets or sets the direction of the transition effect.

        Returns:
            TransitionInOutDirection: The direction of the transition effect.
        """
        GetDllLibPpt().ZoomSlideTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().ZoomSlideTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ZoomSlideTransition_get_Direction,self.Ptr)
        objwraped = TransitionInOutDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionInOutDirection'):
        GetDllLibPpt().ZoomSlideTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ZoomSlideTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current object is equal to another object.

        Args:
            obj: The object to compare with the current object.

        Returns:
            bool: True if the objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ZoomSlideTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ZoomSlideTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ZoomSlideTransition_Equals,self.Ptr, intPtrobj)
        return ret

