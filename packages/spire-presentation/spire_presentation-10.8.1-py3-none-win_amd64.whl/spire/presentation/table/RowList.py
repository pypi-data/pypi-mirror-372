from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class RowList (  SpireObject ) :
    """
    Represents a collection of table rows in a presentation table.
    Inherits from: SpireObject class
    """
    @dispatch
    def __getitem__(self, key):
        """
        Gets the TableRow at the specified index using array syntax.

        Args:
            key (int): The zero-based index of the row to retrieve.

        Returns:
            TableRow: The requested table row object.

        Raises:
            StopIteration: If index is out of range.
        """
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().RowList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().RowList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RowList_get_Item,self.Ptr, key)
        ret = None if intPtr==None else TableRow(intPtr)
        return ret

    def get_Item(self ,index:int)->'TableRow':
        """
        Gets the element at the specified index.

        Args:
            index (int): The zero-based index of the row to retrieve.

        Returns:
            TableRow: The requested table row object.
        """
        
        GetDllLibPpt().RowList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().RowList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RowList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TableRow(intPtr)
        return ret



    def Append(self ,row:'TableRow')->int:
        """
        Adds a new row to the collection.

        Args:
            row (TableRow): The row object to add to the collection.

        Returns:
            int: The index at which the row has been added.
        """
        intPtrrow:c_void_p = row.Ptr

        GetDllLibPpt().RowList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().RowList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().RowList_Append,self.Ptr, intPtrrow)
        return ret


    def Insert(self ,index:int,row:'TableRow'):
        """
        Inserts a row at the specified position in the collection.

        Args:
            index (int): The zero-based index at which row should be inserted.
            row (TableRow): The row object to insert.
        """
        intPtrrow:c_void_p = row.Ptr

        GetDllLibPpt().RowList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().RowList_Insert,self.Ptr, index,intPtrrow)


    def RemoveAt(self ,firstRowIndex:int,withAttachedRows:bool):
        """
        Removes a row at the specified position from the table.

        Args:
            firstRowIndex (int): Index of the row to delete.
            withAttachedRows (bool): True to delete attached rows, False otherwise.
        """
        
        GetDllLibPpt().RowList_RemoveAt.argtypes=[c_void_p ,c_int,c_bool]
        CallCFunction(GetDllLibPpt().RowList_RemoveAt,self.Ptr, firstRowIndex,withAttachedRows)

    @property
    def Count(self)->int:
        """
        Gets the number of rows in the collection.

        Returns:
            int: The actual number of elements in the collection.
        """
        GetDllLibPpt().RowList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().RowList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().RowList_get_Count,self.Ptr)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for iterating through the collection.

        Returns:
            IEnumerator: An enumerator object for the entire collection.
        """
        GetDllLibPpt().RowList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().RowList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RowList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


