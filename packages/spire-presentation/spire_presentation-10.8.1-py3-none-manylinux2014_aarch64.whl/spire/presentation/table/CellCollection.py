from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CellCollection (  PptObject, IActiveSlide) :
    """
    Represents a collection of Cell objects in a table.
    Provides indexed access and enumeration capabilities.
    """

    @dispatch
    def __getitem__(self, key):
        """
        Gets the Cell at the specified index.
        
        Args:
            key (int): Index of the cell to retrieve.
        
        Returns:
            Cell: The cell at the specified index.
        """
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().CellCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CellCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_Item,self.Ptr, key)
        ret = None if intPtr==None else Cell(intPtr)
        return ret

    def get_Item(self ,index:int)->'Cell':
        """
        Gets the Cell at the specified index.
        
        Args:
            index (int): Index of the cell to retrieve.
        
        Returns:
            Cell: The cell at the specified index.
        """
        
        GetDllLibPpt().CellCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CellCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else Cell(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
        Gets the number of cells in the collection.
        Read-only.
        
        Returns:
            int: Total cell count.
        """
        GetDllLibPpt().CellCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellCollection_get_Count,self.Ptr)
        return ret

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide of the collection.
        Read-only.
        
        Returns:
            ActiveSlide: Parent slide object.
        """
        GetDllLibPpt().CellCollection_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation of the collection.
        Read-only.
        
        Returns:
            Presentation: Parent presentation object.
        """
        GetDllLibPpt().CellCollection_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through all cells in the collection.
        
        Returns:
            IEnumerator: Enumerator for cell collection.
        """
        GetDllLibPpt().CellCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


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
#        GetDllLibPpt().CellCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().CellCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).
        
        Returns:
            bool: True if access is thread-safe; otherwise, False.
        """
        GetDllLibPpt().CellCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CellCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: An object that can be used to synchronize access to the collection.
        """
        GetDllLibPpt().CellCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


