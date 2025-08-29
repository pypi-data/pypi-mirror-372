from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeAdjustCollection (  ShapeAdjustmentList, ICollection, IEnumerable) :
    """
    Represents a collection of shape adjustments.
    Inherits from ShapeAdjustmentList and implements collection interfaces.
    """

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is thread-safe.

        Returns:
            bool: True if collection access is synchronized, False otherwise
        """
        GetDllLibPpt().ShapeAdjustCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjustCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeAdjustCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        Returns:
            SpireObject: An object that can be used for synchronization
        """
        GetDllLibPpt().ShapeAdjustCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjustCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeAdjustCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Returns an enumerator that iterates through the collection.

        Returns:
            IEnumerator: An enumerator object for the collection
        """
        GetDllLibPpt().ShapeAdjustCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjustCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeAdjustCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


