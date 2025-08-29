from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
from spire.presentation.collections.TextRangeList import TextRangeList

class TextRangeCollection (  TextRangeList) :
    """
    Represents a collection of a range.
   
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if the current object is equal to another object.

        Args:
            obj: The object to compare with the current object.

        Returns:
            bool: True if the objects are equal; otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextRangeCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextRangeCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextRangeCollection_Equals,self.Ptr, intPtrobj)
        return ret

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is thread-safe.

        Returns:
            bool: True if access is synchronized (thread-safe); otherwise False.
        """
        GetDllLibPpt().TextRangeCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().TextRangeCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextRangeCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.

        Returns:
            SpireObject: An object that can be used for synchronization.
        """
        GetDllLibPpt().TextRangeCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().TextRangeCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRangeCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


