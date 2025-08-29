from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillFormatCollection (  FillFormatList, ICollection) :
    """
    Represents a collection of FillFormat objects.
    
    Provides management capabilities for groups of fill formats with collection 
    functionality including synchronization properties.
    """

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is thread-safe.
        
        Returns:
            bool: True for synchronized access
        """
        GetDllLibPpt().FillFormatCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().FillFormatCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillFormatCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets the synchronization root object.
        
        Returns:
            SpireObject: Object used for synchronization
        """
        GetDllLibPpt().FillFormatCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().FillFormatCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormatCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


