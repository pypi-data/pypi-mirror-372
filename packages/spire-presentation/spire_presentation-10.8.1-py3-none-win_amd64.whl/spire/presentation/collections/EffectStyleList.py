from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectStyleList (  IEnumerable) :
    """
    Base class representing a collection of effect styles with enumeration capabilities.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of elements in the collection (read-only).
        """
        GetDllLibPpt().EffectStyleList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyleList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().EffectStyleList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'EffectStyle':
        """
        Gets the effect style element at the specified position.
        Args:
            index: Zero-based position index of the element.
        Returns:
            EffectStyle object at specified position.
        """
        
        GetDllLibPpt().EffectStyleList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().EffectStyleList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyleList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else EffectStyle(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified SpireObject is equal to the current object.
        Args:
            obj: The SpireObject to compare with the current object.
        Returns:
            True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().EffectStyleList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EffectStyleList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectStyleList_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the collection.
        Returns:
            IEnumerator object for the entire collection.
        """
        GetDllLibPpt().EffectStyleList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyleList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyleList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


