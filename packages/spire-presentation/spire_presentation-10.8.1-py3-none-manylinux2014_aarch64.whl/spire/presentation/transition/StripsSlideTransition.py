from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class StripsSlideTransition (  Transition) :
    """
    Represents a strips-style slide transition effect.
    
    Inherits from base Transition class and adds direction control.
    """
    @property

    def Direction(self)->'TransitionCornerDirection':
        """
        Gets the direction of the transition effect.
        
        Returns:
            TransitionCornerDirection: Current animation direction
        """
        GetDllLibPpt().StripsSlideTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().StripsSlideTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().StripsSlideTransition_get_Direction,self.Ptr)
        objwraped = TransitionCornerDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionCornerDirection'):
        GetDllLibPpt().StripsSlideTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().StripsSlideTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Compares this object with another for equality.
        
        Args:
            obj (SpireObject): Object to compare with
        
        Returns:
            bool: True if objects are equal, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().StripsSlideTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().StripsSlideTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().StripsSlideTransition_Equals,self.Ptr, intPtrobj)
        return ret

