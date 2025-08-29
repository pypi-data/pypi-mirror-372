from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TagCollection (TagList) :
    """
    Represents the collection of tags (user defined pairs of strings)
   
    """

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).

        Returns:
            bool: True if access is synchronized, False otherwise
        """
        GetDllLibPpt().TagCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().TagCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TagCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets a synchronization root.

        Returns:
            SpireObject: An object that can be used to synchronize access
        """
        GetDllLibPpt().TagCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().TagCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TagCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the entire collection.

        Returns:
            IEnumerator: An enumerator for the entire collection
        """
        GetDllLibPpt().TagCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TagCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TagCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


