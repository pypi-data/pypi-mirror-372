from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Transition (  PptObject) :
    """
    Represents slide transition effects in a presentation.

    Methods:
        Equals: Compares with another object for equality.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current Transition object.

        Args:
            obj (SpireObject): The object to compare with.

        Returns:
            bool: True if objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Transition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Transition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Transition_Equals,self.Ptr, intPtrobj)
        return ret

