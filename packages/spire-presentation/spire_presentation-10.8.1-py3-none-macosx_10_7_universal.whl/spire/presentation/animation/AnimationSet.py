from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationSet (  CommonBehavior) :
    """
    Represents a set effect for animation behavior.
    """
    @property

    def To(self)->'SpireObject':
        """
        Gets or sets the target value for the animated attribute after the effect.

        """
        GetDllLibPpt().AnimationSet_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationSet_get_To.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationSet_get_To,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @To.setter
    def To(self, value:'SpireObject'):
        """
        Gets or sets the target value for the animated attribute after the effect.

        """
        GetDllLibPpt().AnimationSet_set_To.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationSet_set_To,self.Ptr, value.Ptr)

