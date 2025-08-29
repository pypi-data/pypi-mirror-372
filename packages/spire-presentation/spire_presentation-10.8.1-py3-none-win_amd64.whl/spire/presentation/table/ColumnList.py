from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ColumnList (  SpireObject) :
    """
    Represents collection of columns in a table.
   
    """

    @dispatch
    def __getitem__(self, key):
        """
        Gets the column at the specified index using indexer syntax.
        
        Args:
            key (int): Zero-based index of the column to retrieve.
        
        Returns:
            TableColumn: The table column at the specified index.
        """
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().ColumnList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ColumnList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColumnList_get_Item,self.Ptr, key)
        ret = None if intPtr==None else TableColumn(intPtr)
        return ret

    def get_Item(self ,index:int)->'TableColumn':
        """
        Gets the column at the specified index.
        
        Args:
            index (int): Zero-based index of the column to retrieve.
        
        Returns:
            TableColumn: The table column at the specified index.
        """
        
        GetDllLibPpt().ColumnList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ColumnList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColumnList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TableColumn(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
        Gets the number of columns in the collection.
        
        Returns:
            int: Number of columns in the collection.
        """
        GetDllLibPpt().ColumnList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ColumnList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColumnList_get_Count,self.Ptr)
        return ret


    def Insert(self ,index:int,template:'TableColumn'):
        """
        Inserts a column into the table at the specified position.
        
        Args:
            index (int): Zero-based index at which to insert the column.
            template (TableColumn): Column template to insert.
        """
        intPtrtemplate:c_void_p = template.Ptr

        GetDllLibPpt().ColumnList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ColumnList_Insert,self.Ptr, index,intPtrtemplate)


    def Add(self ,template:'TableColumn'):
        """
        Adds a column to the end of the table.
        
        Args:
            template (TableColumn): Column template to add.
        """
        intPtrtemplate:c_void_p = template.Ptr

        GetDllLibPpt().ColumnList_Add.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ColumnList_Add,self.Ptr, intPtrtemplate)


    def RemoveAt(self ,firstColumnIndex:int,withAttachedRows:bool):
        """
        Removes a column at the specified position.
        
        Args:
            firstColumnIndex (int): Index of the column to delete.
            withAttachedRows (bool): True to delete attached rows; False otherwise.
        """
        
        GetDllLibPpt().ColumnList_RemoveAt.argtypes=[c_void_p ,c_int,c_bool]
        CallCFunction(GetDllLibPpt().ColumnList_RemoveAt,self.Ptr, firstColumnIndex,withAttachedRows)


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the collection.
        
        Returns:
            IEnumerator: Enumerator object for the entire collection.
        """
        GetDllLibPpt().ColumnList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ColumnList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColumnList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


