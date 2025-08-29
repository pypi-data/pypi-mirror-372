from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TabStop (SpireObject) :
    """
    Represents a tabulation for text formatting.
    
    Attributes:
        Position: Gets or sets the tab position in points.
        Alignment: Gets or sets the alignment style of the tab.
    """
    @property
    def Position(self)->float:
        """
        Gets or sets position of a tab.
        Assigning this property can change tab's index in collection and invalidate Enumerator.

        Returns:
            float: The tab position in points (read/write).
        """
        GetDllLibPpt().TabStop_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().TabStop_get_Position.restype=c_double
        ret = CallCFunction(GetDllLibPpt().TabStop_get_Position,self.Ptr)
        return ret

    @Position.setter
    def Position(self, value:float):
        """
        Sets position of a tab.

        Args:
            value: New tab position in points (float).
        """
        GetDllLibPpt().TabStop_set_Position.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().TabStop_set_Position,self.Ptr, value)

    @property

    def Alignment(self)->'TabAlignmentType':
        """
        Gets or sets align style of a tab.

        Returns:
            TabAlignmentType: The alignment type of the tab (read/write).
        """
        GetDllLibPpt().TabStop_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().TabStop_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStop_get_Alignment,self.Ptr)
        objwraped = TabAlignmentType(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'TabAlignmentType'):
        """
        Sets align style of a tab.

        Args:
            value: New alignment type (TabAlignmentType).
        """
        GetDllLibPpt().TabStop_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TabStop_set_Alignment,self.Ptr, value.value)


    def CompareTo(self ,obj:'SpireObject')->int:
        """
        Compares the current instance with another object of the same type.

        Args:
            obj: An object to compare with this instance.

        Returns:
            int: A 32-bit integer that indicates the relative order of the comparands.
                < 0: This instance is less than obj.
                =0:This instance is equal to obj.
                >0:This instance is greater than obj.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TabStop_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TabStop_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStop_CompareTo,self.Ptr, intPtrobj)
        return ret

