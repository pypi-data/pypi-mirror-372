from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStopCollection (  GradientStopList) :
    """
    Represents a collection of gradient stops.

    """


    @property
    def IsSynchronized(self)->bool:
        """
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    
        """
        GetDllLibPpt().GradientStopCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GradientStopCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets a synchronization root.
            
        """
        GetDllLibPpt().GradientStopCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


