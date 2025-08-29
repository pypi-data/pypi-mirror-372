from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillStyleList (  FillListBase) :
    """
    Represents a collection of fill styles used in presentation themes.
    
    Provides base functionality for accessing and managing fill style elements.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current collection is equal to another object.
        
        Args:
            obj: The object to compare with
        
        Returns:
            bool: True if the objects are equal, otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillStyleList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillStyleList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillStyleList_Equals,self.Ptr, intPtrobj)
        return ret

