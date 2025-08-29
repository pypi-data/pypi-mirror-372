from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectStyleCollection (  EffectStyleList, ICollection) :
    """
    Represents a collection of effect styles that inherit functionality from EffectStyleList and ICollection interfaces.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified SpireObject is equal to the current object.
        Args:
            obj: The SpireObject to compare with the current object.
        Returns:
            True if the objects are equal; otherwise, False.

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().EffectStyleCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EffectStyleCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectStyleCollection_Equals,self.Ptr, intPtrobj)
        return ret

#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all elements from the collection to the specified array.
#    </summary>
#    <param name="array">Target array.</param>
#    <param name="index">Starting index in the target array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().EffectStyleCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().EffectStyleCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).
        
        Returns:
            bool: True if access is thread-safe, False otherwise.
        """
        GetDllLibPpt().EffectStyleCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyleCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectStyleCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets the synchronization root object for thread-safe access.
        
        Returns:
            SpireObject: An object that can be used to synchronize access to the collection.
        """
        GetDllLibPpt().EffectStyleCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyleCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyleCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


