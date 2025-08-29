from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNodes (  IEnumerable) :
    """
    Represents a collection of TimeNode objects in a presentation animation sequence.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of TimeNode objects contained in the collection.
        
        Returns:
            int: The number of time nodes in the collection.
        """
        GetDllLibPpt().TimeNodes_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodes_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TimeNodes_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TimeNode':
        """
        Gets the TimeNode at the specified index position.
        
        Args:
            index: The zero-based index of the element to retrieve.
            
        Returns:
            TimeNode: The TimeNode at the specified index.
        """
        
        GetDllLibPpt().TimeNodes_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TimeNodes_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeNodes_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TimeNode(intPtr)
        return ret



    def RemoveAt(self ,index:int):
        """
        Removes the TimeNode at the specified index position from the collection.
        
        Args:
            index: The zero-based index of the element to remove.
        """
        
        GetDllLibPpt().TimeNodes_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().TimeNodes_RemoveAt,self.Ptr, index)


    def Remove(self ,node:'TimeNode'):
        """
        Removes the first occurrence of a specific TimeNode from the collection.
        
        Args:
            node: The TimeNode to remove from the collection.
        """
        intPtrnode:c_void_p = node.Ptr

        GetDllLibPpt().TimeNodes_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().TimeNodes_Remove,self.Ptr, intPtrnode)

    def Clear(self):
        """
        Removes all TimeNode objects from the collection.
        """
        GetDllLibPpt().TimeNodes_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TimeNodes_Clear,self.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified SpireObject is equal to the current TimeNodes collection.
        
        Args:
            obj: The SpireObject to compare with the current object.
            
        Returns:
            bool: True if the specified object is equal to the current object; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeNodes_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeNodes_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNodes_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Returns an enumerator that iterates through the TimeNodes collection.
        
        Returns:
            IEnumerator: An enumerator that can be used to iterate through the collection.
        """
        GetDllLibPpt().TimeNodes_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodes_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeNodes_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


