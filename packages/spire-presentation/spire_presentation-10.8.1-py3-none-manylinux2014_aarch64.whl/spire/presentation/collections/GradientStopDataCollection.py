from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStopDataCollection (  ICollection, IEnumerable) :
    """
    Represents a collection of GradientStopData objects.
    
    """
    @property
    def Count(self)->int:
        """
        Gets the number of gradient stops in a collection.
            
        """
        GetDllLibPpt().GradientStopDataCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopDataCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopDataCollection_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'GradientStopData':
        """
        Gets the gradient stop by index.
 
        """
        
        GetDllLibPpt().GradientStopDataCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().GradientStopDataCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopDataCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else GradientStopData(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the entire collection.
   
        """
        GetDllLibPpt().GradientStopDataCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopDataCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopDataCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property
    def IsSynchronized(self)->bool:
        """
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
   
        """
        GetDllLibPpt().GradientStopDataCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopDataCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GradientStopDataCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets a synchronization root.
           
        """
        GetDllLibPpt().GradientStopDataCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopDataCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopDataCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


