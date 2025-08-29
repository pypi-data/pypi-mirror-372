from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartCategory (  PptObject) :
    """
    Represents chart categories in a presentation.
    
    """
    @property

    def DataRange(self)->'CellRange':
        """
        Gets or sets the CellRange object associated with this chart category.
        
        Returns:
            CellRange: The cell range defining the category's data source.
        """
        GetDllLibPpt().ChartCategory_get_DataRange.argtypes=[c_void_p]
        GetDllLibPpt().ChartCategory_get_DataRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartCategory_get_DataRange,self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @DataRange.setter
    def DataRange(self, value:'CellRange'):
        """
        Sets the CellRange object for this chart category.
        
        Args:
            value (CellRange): The new cell range to associate with this category.
        """
        GetDllLibPpt().ChartCategory_set_DataRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategory_set_DataRange,self.Ptr, value.Ptr)

