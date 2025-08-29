from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MasterSlideCollection (  MasterSlideList) :
    """Represents a collection of master slides."""

    @property
    def IsSynchronized(self)->bool:
        """
        Gets a value indicating whether access to the collection is thread-safe.
        
        Returns:
            bool: True if thread-safe, otherwise False
        """
        GetDllLibPpt().MasterSlideCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().MasterSlideCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().MasterSlideCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: Synchronization root object
        """
        GetDllLibPpt().MasterSlideCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().MasterSlideCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterSlideCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


