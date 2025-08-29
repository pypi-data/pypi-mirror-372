from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShredTransition (  Transition) :
    """
    Represents a shred paper transition effect between slides.
    
    Inherits from Transition base class and controls the shredding direction.
    """
    @property

    def Direction(self)->'TransitionShredInOutDirection':
        """
        Gets or sets the shred direction.
        
        Returns:
            TransitionShredInOutDirection: Current shred direction.
        """
        GetDllLibPpt().ShredTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().ShredTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShredTransition_get_Direction,self.Ptr)
        objwraped = TransitionShredInOutDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionShredInOutDirection'):
        GetDllLibPpt().ShredTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShredTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if objects are equivalent.
        
        Args:
            obj: Object to compare with.
            
        Returns:
            bool: True if objects are equal.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShredTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShredTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShredTransition_Equals,self.Ptr, intPtrobj)
        return ret

