from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectDataCollection (  ICollection, IEnumerable) :
    """
    Represents a readonly collection of EffectData objects.
    
    This collection provides access to effect data nodes in a presentation.
    
    Attributes:
        Count (int): Gets the number of image effects in the collection (read-only).
        IsSynchronized (bool): Indicates whether access to the collection is thread-safe.
        SyncRoot (SpireObject): Gets an object that can be used to synchronize access to the collection.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of image effects in the collection.
        """
        GetDllLibPpt().EffectDataCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().EffectDataCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().EffectDataCollection_get_Count,self.Ptr)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the collection.
        
        Returns:
            IEnumerator: An enumerator for the entire collection.
        """
        GetDllLibPpt().EffectDataCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().EffectDataCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDataCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    def get_Item(self ,index:int)->'EffectNode':
        """
        Gets the EffectNode at the specified index position.
        
        Args:
            index: The zero-based index of the element to get.
            
        Returns:
            EffectNode: The EffectNode at the specified index.
        """
        
        GetDllLibPpt().EffectDataCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().EffectDataCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDataCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else EffectNode(intPtr)
        return ret


#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all elements from the collection into the specified array.
#    </summary>
#    <param name="array">Array to fill.</param>
#    <param name="index">Starting position in target array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().EffectDataCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().EffectDataCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).
        """
        GetDllLibPpt().EffectDataCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().EffectDataCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectDataCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        """
        GetDllLibPpt().EffectDataCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().EffectDataCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDataCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


