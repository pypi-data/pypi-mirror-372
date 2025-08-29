from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TableColumn (  CellCollection) :
    """
    Represents a column in a table structure.
    
    This class provides access to properties and methods for manipulating
    table columns, including column width adjustment.
    """
    @property
    def Width(self)->float:
        """
        Gets or sets the width of the column.
        
        Returns:
            float: The current width of the column in points.
        """
        GetDllLibPpt().TableColumn_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().TableColumn_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibPpt().TableColumn_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        """
        Sets the width of the column.
        
        Args:
            value (float): The new width value in points.
        """
        GetDllLibPpt().TableColumn_set_Width.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().TableColumn_set_Width,self.Ptr, value)

