from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LegendEntryCollection (SpireObject) :
    """
    Represents a collection of chart series data formats.

    This class provides access to legend entries in a chart, allowing retrieval of individual entries by index.

    Example:
        collection = chart.legend.entries
        first_entry = collection[0]
    """

    def get_Item(self ,index:int)->'LegendEntry':
        """
        Gets the element at the specified index.

        Args:
            index: The zero-based index of the element to get

        Returns:
            LegendEntry: The legend entry at the specified index
        """
        
        GetDllLibPpt().LegendEntryCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().LegendEntryCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LegendEntryCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else LegendEntry(intPtr)
        return ret
    

    @property
    def Count(self)->int:
        """
        Gets the number of elements contained in the collection.

        Returns:
            int: The total number of legend entries in the collection
        """
        
        GetDllLibPpt().LegendEntryCollection_GetCount.argtypes=[c_void_p]
        GetDllLibPpt().LegendEntryCollection_GetCount.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LegendEntryCollection_GetCount,self.Ptr)
        return ret


