from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OleObjectCollection (  ICollection, IEnumerable) :
    """
    Represents a collection of OLE object controls embedded in a presentation.
    This collection provides methods to manage and manipulate OLE objects within a slide.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of OLE objects contained in the collection.
        
        Returns:
            int: The total number of OLE objects in the collection.
        """
        GetDllLibPpt().OleObjectCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().OleObjectCollection_get_Count,self.Ptr)
        return ret


    def Remove(self ,item:'OleObject'):
        """
        Removes a specific OLE object from the collection.
        
        Args:
            item (OleObject): The OLE object to remove from the collection.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().OleObjectCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().OleObjectCollection_Remove,self.Ptr, intPtritem)


    def RemoveAt(self ,index:int):
        """
        Removes the OLE object at the specified index location.
        
        Args:
            index (int): The zero-based index of the OLE object to remove.
        """
        
        GetDllLibPpt().OleObjectCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().OleObjectCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
        Removes all OLE objects from the collection.
        """
        GetDllLibPpt().OleObjectCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().OleObjectCollection_Clear,self.Ptr)


    def get_Item(self ,index:int)->'OleObject':
        """
        Retrieves the OLE object at the specified index position.
        
        Args:
            index (int): The zero-based index of the OLE object to retrieve.
        
        Returns:
            OleObject: The OLE object at the specified index.
        """
        
        GetDllLibPpt().OleObjectCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().OleObjectCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else OleObject(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Returns an enumerator that iterates through the collection.
        
        Returns:
            IEnumerator: An enumerator that can be used to iterate through the collection.
        """
        GetDllLibPpt().OleObjectCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).
        
        Returns:
            bool: True if access is thread-safe; otherwise, False.
        """
        GetDllLibPpt().OleObjectCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OleObjectCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: An object that can be used to synchronize access to the collection.
        """
        GetDllLibPpt().OleObjectCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


