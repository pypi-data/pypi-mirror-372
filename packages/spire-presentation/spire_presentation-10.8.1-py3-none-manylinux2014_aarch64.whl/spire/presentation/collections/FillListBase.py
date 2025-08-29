from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillListBase (  IEnumerable) :
    """
    Represents a collection of FillFormat objects used in presentations.
    
    Provides access to fill formats through enumeration and indexing.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of FillFormat elements actually contained in the collection.
        
        Returns:
            int: The number of elements in the collection.
        """
        GetDllLibPpt().FillListBase_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().FillListBase_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillListBase_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'FillFormat':
        """
        Retrieves the FillFormat element at the specified index.
        
        Args:
            index: Zero-based index of the element to retrieve
        
        Returns:
            FillFormat: The fill format at the specified position
        """
        GetDllLibPpt().FillListBase_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().FillListBase_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillListBase_get_Item,self.Ptr, index)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current collection is equal to another object.
        
        Args:
            obj: The object to compare with
        
        Returns:
            bool: True if the objects are equal, otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillListBase_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillListBase_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillListBase_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the collection.
        
        Returns:
            IEnumerator: Enumerator for iterating through FillFormat objects
        """
        GetDllLibPpt().FillListBase_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().FillListBase_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillListBase_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


