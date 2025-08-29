from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class WheelSlideTransition (  Transition) :
    """Represents a wheel slide transition effect."""
    @property
    def Spokes(self)->int:
        """
        Gets or sets the number of spokes in the wheel transition.

        Returns:
            int: The number of spokes in the wheel.
        """
        GetDllLibPpt().WheelSlideTransition_get_Spokes.argtypes=[c_void_p]
        GetDllLibPpt().WheelSlideTransition_get_Spokes.restype=c_int
        ret = CallCFunction(GetDllLibPpt().WheelSlideTransition_get_Spokes,self.Ptr)
        return ret

    @Spokes.setter
    def Spokes(self, value:int):
        GetDllLibPpt().WheelSlideTransition_set_Spokes.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().WheelSlideTransition_set_Spokes,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current object is equal to another object.

        Args:
            obj: The object to compare with the current object.

        Returns:
            bool: True if the objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().WheelSlideTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().WheelSlideTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().WheelSlideTransition_Equals,self.Ptr, intPtrobj)
        return ret

