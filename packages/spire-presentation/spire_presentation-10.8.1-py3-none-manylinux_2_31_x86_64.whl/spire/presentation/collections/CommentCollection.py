from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommentCollection (  CommentList) :
    """
    Represents a collection of comments of one author.
    
    Inherits from CommentList and provides thread-safety properties.
    """

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).
        
        Returns:
            bool: True if access is thread-safe, False otherwise.
        """
        GetDllLibPpt().CommentCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().CommentCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CommentCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets the synchronization root object for thread-safe access.
        
        Returns:
            SpireObject: An object that can be used to synchronize access to the collection.
        """
        GetDllLibPpt().CommentCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().CommentCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


