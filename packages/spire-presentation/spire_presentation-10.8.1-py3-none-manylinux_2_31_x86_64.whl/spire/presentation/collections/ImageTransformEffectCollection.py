from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ImageTransformEffectCollection (  ImageTransform, ICollection) :
    """
    Represents a collection of effects apllied to an image.
    
    """

    @property
    def IsSynchronized(self)->bool:
        """
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    
        """
        GetDllLibPpt().ImageTransformEffectCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransformEffectCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ImageTransformEffectCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets a synchronization root.
         
        """
        GetDllLibPpt().ImageTransformEffectCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransformEffectCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransformEffectCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


