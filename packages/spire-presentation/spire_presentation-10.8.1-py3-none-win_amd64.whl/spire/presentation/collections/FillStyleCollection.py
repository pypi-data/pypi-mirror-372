from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillStyleCollection (  FillStyleList, ICollection) :
    """
    Represents a thread-safe collection of fill styles used in presentation themes.
    
    Implements additional synchronization capabilities for multi-threaded access.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current collection is equal to another object.
        
        Args:
            obj: The object to compare with
        
        Returns:
            bool: True if the objects are equal, otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillStyleCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillStyleCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillStyleCollection_Equals,self.Ptr, intPtrobj)
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
#        GetDllLibPpt().FillStyleCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().FillStyleCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is thread-safe.
        
        Returns:
            bool: True if synchronized (thread-safe), otherwise False
        """
        GetDllLibPpt().FillStyleCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().FillStyleCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillStyleCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: Synchronization root object
        """
        GetDllLibPpt().FillStyleCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().FillStyleCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillStyleCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


