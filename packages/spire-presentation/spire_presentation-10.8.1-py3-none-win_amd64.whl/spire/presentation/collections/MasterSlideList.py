from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MasterSlideList (SpireObject) :
    """
    Represents a collection of master slides.
     
    """
    @property
    def Count(self)->int:
        """
        Gets the number of elements in the collection.
        
        Returns:
            int: Number of master slides
        """
        GetDllLibPpt().MasterSlideList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().MasterSlideList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MasterSlideList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        """
        Gets the master slide at the specified index.
        
        Args:
            index (int): Zero-based index
            
        Returns:
            IMasterSlide: Master slide at specified position
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().MasterSlideList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().MasterSlideList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterSlideList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IMasterSlide(intPtr)
        return ret

    def get_Item(self ,index:int)->'IMasterSlide':
        """
        Gets the master slide at the specified index.
        
        Args:
            index (int): Zero-based index
            
        Returns:
            IMasterSlide: Master slide at specified position
        """
        
        GetDllLibPpt().MasterSlideList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().MasterSlideList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterSlideList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IMasterSlide(intPtr)
        return ret



    def Remove(self ,value:'IMasterSlide'):
        """
        Removes the first occurrence of a specific master slide.
        
        Args:
            value (IMasterSlide): Master slide to remove
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().MasterSlideList_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().MasterSlideList_Remove,self.Ptr, intPtrvalue)


    def RemoveAt(self ,index:int):
        """
        Removes the master slide at the specified index.
        
        Args:
            index (int): Zero-based index of element to remove
        """
        
        GetDllLibPpt().MasterSlideList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().MasterSlideList_RemoveAt,self.Ptr, index)

    def CleanupDesigns(self):
        """Removes unused master slides from the collection."""
        GetDllLibPpt().MasterSlideList_CleanupDesigns.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().MasterSlideList_CleanupDesigns,self.Ptr)


    def AppendSlide(self ,slide:'IMasterSlide')->int:
        """
        Appends a new master slide to the end of the collection.
        
        Args:
            slide (IMasterSlide): Master slide to add
            
        Returns:
            int: Index of the newly added slide
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().MasterSlideList_AppendSlide.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().MasterSlideList_AppendSlide.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MasterSlideList_AppendSlide,self.Ptr, intPtrslide)
        return ret


    def InsertSlide(self ,index:int,slide:'IMasterSlide'):
        """
        Inserts a master slide at the specified index.
        
        Args:
            index (int): Zero-based insertion position
            slide (IMasterSlide): Master slide to insert
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().MasterSlideList_InsertSlide.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().MasterSlideList_InsertSlide,self.Ptr, index,intPtrslide)


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the collection.
        
        Returns:
            IEnumerator: Enumerator object
        """
        GetDllLibPpt().MasterSlideList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().MasterSlideList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterSlideList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


