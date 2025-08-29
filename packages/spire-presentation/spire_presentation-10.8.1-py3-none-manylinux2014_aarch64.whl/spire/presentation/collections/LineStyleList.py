from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineStyleList (  IEnumerable) :
    """
    Represents a collection of line formatting styles.
    
    This class provides enumeration capabilities for a collection of line styles.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of line styles in the collection.
        
        Returns:
            int: The actual number of elements in the collection.
        """
        GetDllLibPpt().LineStyleList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().LineStyleList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LineStyleList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TextLineFormat':
        """
        Gets the line style at the specified index.
        
        Args:
            index (int): The zero-based index of the element to get.
            
        Returns:
            TextLineFormat: The line style at the specified index.
        """
        
        GetDllLibPpt().LineStyleList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().LineStyleList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineStyleList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current LineStyleList.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LineStyleList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LineStyleList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LineStyleList_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the collection.
        
        Returns:
            IEnumerator: An enumerator that can be used to iterate through the collection.
        """
        GetDllLibPpt().LineStyleList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().LineStyleList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineStyleList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


