from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TableRow (  CellCollection) :
    """
    Represents a single row within a table structure.
    
    This class provides access to row-specific properties such as height,
    and methods for row manipulation within table layouts.
    """
    @property
    def Height(self)->float:
        """
        Gets or sets the height of the row.
        
        Returns:
            float: The current height of the row in points.
        """
        GetDllLibPpt().TableRow_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().TableRow_get_Height.restype=c_double
        ret = CallCFunction(GetDllLibPpt().TableRow_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        """
        Sets the height of the row.
        
        Args:
            value (float): The new height value in points.
        """
        GetDllLibPpt().TableRow_set_Height.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().TableRow_set_Height,self.Ptr, value)

