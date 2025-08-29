from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TabData (SpireObject) :
    """
    Represents a text's tabulation stop.
    """
    @property
    def Position(self)->float:
        """
        Gets or sets the tab position.
        
        Returns:
            float: The position of the tab.
        """
        GetDllLibPpt().TabData_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().TabData_get_Position.restype=c_double
        ret = CallCFunction(GetDllLibPpt().TabData_get_Position,self.Ptr)
        return ret

    @property

    def Alignment(self)->'TabAlignmentType':
        """
        Gets or sets the alignment style of the tab.
        
        Returns:
            TabAlignmentType: The alignment type of the tab.
        """
        GetDllLibPpt().TabData_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().TabData_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabData_get_Alignment,self.Ptr)
        objwraped = TabAlignmentType(ret)
        return objwraped


    def CompareTo(self ,obj:'SpireObject')->int:
        """
        Compares the current instance with another object of the same type.
        
        Args:
            obj (SpireObject): An object to compare with this instance.
            
        Returns:
            int: A 32-bit integer that indicates the relative order of the comparands:
                - < 0 : This instance is less than obj
                - = 0 : This instance is equal to obj
                - > 0 : This instance is greater than obj
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TabData_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TabData_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabData_CompareTo,self.Ptr, intPtrobj)
        return ret

