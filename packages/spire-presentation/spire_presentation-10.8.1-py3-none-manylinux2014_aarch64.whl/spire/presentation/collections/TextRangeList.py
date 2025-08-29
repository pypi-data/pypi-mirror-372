from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class TextRangeList (SpireObject) :

    """
    Represents a collection of text ranges within presentation text elements.
    
    Provides list-like access to text fragments with formatting properties.
    """

    def __getitem__(self ,index:int)->'TextRange':
        """Gets text range at the specified position.
        
        Args:
            index: Zero-based index of the text range
            
        Returns:
            TextRange object at the specified index.
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().TextRangeList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextRangeList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRangeList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret

    @property
    def Count(self)->int:
        """
        Gets number of text ranges in the collection.
        
        Returns:
            Integer count of text range objects.
        """
        GetDllLibPpt().TextRangeList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TextRangeList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextRangeList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TextRange':
        """
        Gets text range at the specified position (alternative accessor).
        
        Args:
            index: Zero-based index of the text range
            
        Returns:
            TextRange object at the specified index.
        """
        
        GetDllLibPpt().TextRangeList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextRangeList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRangeList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret



    def Append(self ,value:'TextRange')->int:
        """
        Adds a text range to the end of collection.
        
        Args:
            value: TextRange object to add
            
        Returns:
            Index position where the range was added.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().TextRangeList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextRangeList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextRangeList_Append,self.Ptr, intPtrvalue)
        return ret


    def Insert(self ,index:int,value:'TextRange'):
        """
        Inserts text range at specified position.
        
        Args:
            index: Insertion position (0-based)
            value: TextRange object to insert
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().TextRangeList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().TextRangeList_Insert,self.Ptr, index,intPtrvalue)

    def Clear(self):
        """Removes all text ranges from the collection."""
        GetDllLibPpt().TextRangeList_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TextRangeList_Clear,self.Ptr)


    def RemoveAt(self ,index:int):
        """
        Removes text range at specified position.
        
        Args:
            index: Zero-based index of range to remove
        """
        
        GetDllLibPpt().TextRangeList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().TextRangeList_RemoveAt,self.Ptr, index)


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets enumerator for iterating through text ranges.
        
        Returns:
            Enumerator object for the collection.
        """
        GetDllLibPpt().TextRangeList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TextRangeList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRangeList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """Determines collection equality with another object.
        
        Args:
            obj: SpireObject to compare with
            
        Returns:
            True if collections are equivalent, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextRangeList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextRangeList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextRangeList_Equals,self.Ptr, intPtrobj)
        return ret

