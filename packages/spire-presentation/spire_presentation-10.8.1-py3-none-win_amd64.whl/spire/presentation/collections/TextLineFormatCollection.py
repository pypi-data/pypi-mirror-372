from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextLineFormatCollection (  TextLineFormatList, ICollection) :
    """
    Represents a collection of LineFormat objects.
  
    """

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).
        
        Returns:
            bool: True if access is thread-safe; otherwise, False.
        """
        GetDllLibPpt().TextLineFormatCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormatCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextLineFormatCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: An object that can be used to synchronize access to the collection.
        """
        GetDllLibPpt().TextLineFormatCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormatCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormatCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


