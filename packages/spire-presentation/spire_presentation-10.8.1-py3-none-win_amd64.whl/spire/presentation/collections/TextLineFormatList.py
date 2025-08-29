from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextLineFormatList (  IEnumerable) :
    """
    Represents a collection of LineFormat objects.
    
    Attributes:
        Count (int): Gets the number of elements actually contained in the collection.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of elements actually contained in the collection.
        
        Returns:
            int: The number of elements in the collection.
        """
        GetDllLibPpt().TextLineFormatList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormatList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormatList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TextLineFormat':
        """
        Gets the element at the specified index.
        
        Args:
            index (int): The zero-based index of the element to get.
            
        Returns:
            TextLineFormat: The element at the specified index.
        """
        GetDllLibPpt().TextLineFormatList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextLineFormatList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormatList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets the enumerator for the entire collection.
        
        Returns:
            IEnumerator: An enumerator that iterates through the collection.
        """
        GetDllLibPpt().TextLineFormatList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormatList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormatList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


