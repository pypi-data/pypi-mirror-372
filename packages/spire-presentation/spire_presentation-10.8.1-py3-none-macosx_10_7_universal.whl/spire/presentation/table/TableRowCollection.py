from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TableRowCollection (  RowList) :
    """
    Represents a collection of table rows within a table structure.
    
    This class provides methods for accessing and managing multiple rows
    in a table, including synchronization properties for thread safety.
    """

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is thread-safe.
        
        Returns:
            bool: True if access is synchronized (thread-safe), otherwise False.
        """
        GetDllLibPpt().TableRowCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().TableRowCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TableRowCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: An object that can be used for synchronization.
        """
        GetDllLibPpt().TableRowCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().TableRowCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TableRowCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


