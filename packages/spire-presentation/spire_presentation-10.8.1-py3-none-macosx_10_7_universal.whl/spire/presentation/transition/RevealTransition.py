from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class RevealTransition (  Transition) :
    """
    Represents the Reveal slide transition effect.
    Inherits from: Transition class
    """
    @property

    def Direction(self)->'TransitionRevealLRDirection':
        """
        Gets or sets the direction of the Reveal transition effect.

        Returns:
            TransitionRevealLRDirection: The current direction setting of the transition.
        """
        GetDllLibPpt().RevealTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().RevealTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().RevealTransition_get_Direction,self.Ptr)
        objwraped = TransitionRevealLRDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionRevealLRDirection'):
        GetDllLibPpt().RevealTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().RevealTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current RevealTransition is equal to another object.

        Args:
            obj (SpireObject): The object to compare with.

        Returns:
            bool: True if the objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().RevealTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().RevealTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().RevealTransition_Equals,self.Ptr, intPtrobj)
        return ret

