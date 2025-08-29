from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommentAuthorCollection (  CommentAuthorList) :
    """
    Represents a collection of comment authors. Inherits from CommentAuthorList.
    
    Attributes:
        IsSynchronized (bool): Indicates whether access to the collection is thread-safe.
        SyncRoot (SpireObject): Gets an object that can be used to synchronize access to the collection.
    """
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
#        GetDllLibPpt().CommentAuthorCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().CommentAuthorCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).
        
        Returns:
            bool: True if access is synchronized; otherwise False.
        """
        GetDllLibPpt().CommentAuthorCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().CommentAuthorCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CommentAuthorCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets a synchronization root object.
        
        Returns:
            SpireObject: Object that can be used to synchronize access to the collection.
        """
        GetDllLibPpt().CommentAuthorCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().CommentAuthorCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


