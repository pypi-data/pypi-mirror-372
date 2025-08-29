from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CellRanges (  SpireObject ) :
    """
    Represents a collection of CellRange objects.
    Provides methods to add, remove, and access cell ranges.
    """

    @dispatch
    def __getitem__(self, index):
        """
        Gets the CellRange at the specified index.
        
        Args:
            index (int): Index of the cell range to retrieve.
        
        Returns:
            CellRange: The cell range at the specified index.
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().CellRanges_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CellRanges_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellRanges_get_Item,self.Ptr, index)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret

    def get_Item(self ,index:int)->'CellRange':
        """
        Gets the CellRange at the specified index.
        
        Args:
            index (int): Index of the cell range to retrieve.
        
        Returns:
            CellRange: The cell range at the specified index.
        """
        
        GetDllLibPpt().CellRanges_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CellRanges_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellRanges_get_Item,self.Ptr, index)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret
    

    def Add(self ,cellRange:'CellRange')->int:
        """
        Adds a new CellRange to the collection.
        
        Args:
            cellRange (CellRange): The cell range to add.
        
        Returns:
            int: Index of the newly added cell range.
        """
        intPtrcellRange:c_void_p = cellRange.Ptr

        GetDllLibPpt().CellRanges_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CellRanges_Add.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRanges_Add,self.Ptr, intPtrcellRange)
        return ret

    
    def AddObject(self ,value:SpireObject)->int:
        """
        Creates a CellRange from a SpireObject and adds it to the collection.
        
        Args:
            value (SpireObject): The object to convert to a cell range.
        
        Returns:
            int: Index of the newly added cell range.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().CellRanges_AddV.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CellRanges_AddV.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRanges_AddV,self.Ptr, intPtrvalue)
        return ret


    def RemoveAt(self ,index:int):
        """
        Removes the cell range at the specified index.
        
        Args:
            index (int): Index of the cell range to remove.
        """
        
        GetDllLibPpt().CellRanges_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().CellRanges_RemoveAt,self.Ptr, index)


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the entire collection.
        
        Returns:
            IEnumerator: Enumerator for cell ranges.
        """
        GetDllLibPpt().CellRanges_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CellRanges_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellRanges_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
        Gets the number of cell ranges in the collection.
        
        Returns:
            int: Total count of cell ranges.
        """
        GetDllLibPpt().CellRanges_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CellRanges_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRanges_get_Count,self.Ptr)
        return ret

