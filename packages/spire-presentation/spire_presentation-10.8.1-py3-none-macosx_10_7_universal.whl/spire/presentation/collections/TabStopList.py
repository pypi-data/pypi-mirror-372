from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TabStopList (SpireObject) :
    """
    Represents a collection of tabs.

    Attributes:
        Count (int): Gets the number of elements actually contained in the collection.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of properties contained in the collection.
        
        Returns:
            int: The total number of properties in the collection.
        """
        GetDllLibPpt().TabStopList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TabStopList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStopList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TabStop':
        """
        Gets the element at the specified index.

        Args:
            index: The zero-based index of the element to retrieve

        Returns:
            TabStop: The element at the specified index
        """
        
        GetDllLibPpt().TabStopList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TabStopList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TabStopList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TabStop(intPtr)
        return ret



    def Append(self ,value:'TabStop')->int:
        """
        Adds a Tab to the collection.

        Args:
            value: The Tab object to be added at the end of the collection

        Returns:
            int: The index at which the tab was added
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().TabStopList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TabStopList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStopList_Append,self.Ptr, intPtrvalue)
        return ret

    def Clear(self):
        """Removes all elements from the collection."""
        GetDllLibPpt().TabStopList_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TabStopList_Clear,self.Ptr)


    def RemoveAt(self ,index:int):
        """
        Removes the element at the specified index.

        Args:
            index: The zero-based index of the element to remove
        """
        
        GetDllLibPpt().TabStopList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().TabStopList_RemoveAt,self.Ptr, index)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Indicates whether two Tabs instances are equal.

        Args:
            obj: The Tabs to compare with the current Tabs

        Returns:
            bool: True if the specified Tabs is equal to the current Tabs, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TabStopList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TabStopList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TabStopList_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
        Gets hash code for this object.

        Returns:
            int: The hash code for this object
        """
        GetDllLibPpt().TabStopList_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().TabStopList_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStopList_GetHashCode,self.Ptr)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the entire collection.

        Returns:
            IEnumerator: An enumerator for the entire collection
        """
        GetDllLibPpt().TabStopList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TabStopList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TabStopList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


