from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeAnimationValueCollection (  IEnumerable) :
    """
    Represents a collection of animation points.
    """
    @property
    def Count(self)->int:
        """Gets the number of points in the collection."""
        GetDllLibPpt().TimeAnimationValueCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValueCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TimeAnimationValueCollection_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TimeAnimationValue':
        """
        Gets a point at the specified index.
        
        Args:
            index: The index of the point to retrieve
            
        Returns:
            TimeAnimationValue: The animation point at the specified index
        """
        
        GetDllLibPpt().TimeAnimationValueCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TimeAnimationValueCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeAnimationValueCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TimeAnimationValue(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an iterator for the collection.
        
        Returns:
            IEnumerator: An iterator for traversing the collection
        """
        GetDllLibPpt().TimeAnimationValueCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValueCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeAnimationValueCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


