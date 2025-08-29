from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineStyleCollection (  LineStyleList, ICollection) :
    """
    Represents a collection of line styles in a presentation.
    
    This class provides thread-safe access to a collection of line formatting styles.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current LineStyleCollection.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LineStyleCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LineStyleCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LineStyleCollection_Equals,self.Ptr, intPtrobj)
        return ret


    @property
    def IsSynchronized(self)->bool:
        """
        Checks whether access to the collection is thread-safe.
        
        Returns:
            bool: True if access is synchronized (thread-safe); otherwise, False.
        """
        GetDllLibPpt().LineStyleCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().LineStyleCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LineStyleCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: An object that can be used for synchronization.
        """
        GetDllLibPpt().LineStyleCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().LineStyleCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineStyleCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


