from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNodeMedia (TimeNode) :
    """
    Represents a media time node in a presentation animation sequence.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified SpireObject is equal to the current TimeNodeMedia.
        
        Args:
            obj: The SpireObject to compare with the current object.
            
        Returns:
            bool: True if the specified object is equal to the current object; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeNodeMedia_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeNodeMedia_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNodeMedia_Equals,self.Ptr, intPtrobj)
        return ret

