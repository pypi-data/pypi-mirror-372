from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ImageTransform (  IEnumerable, IActiveSlide, IActivePresentation) :
    """
    Represents a collection of effects applied to an image.
    
    This class provides functionality to manage image transformation effects such as 
    adding, removing, and accessing individual effects in a collection.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of image effects in the collection.
        
        Args:
            None
        
        Returns:
            int: The number of image effects in the collection
        """
        GetDllLibPpt().ImageTransform_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransform_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ImageTransform_get_Count,self.Ptr)
        return ret


    def RemoveAt(self ,index:int):
        """
        Removes an image effect from the collection at the specified index.
        
        Args:
            index (int): Zero-based index of the effect to remove
        """
        
        GetDllLibPpt().ImageTransform_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ImageTransform_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
        Removes all image effects from the collection.
        """
        GetDllLibPpt().ImageTransform_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ImageTransform_Clear,self.Ptr)


    def Add(self ,base:'ImageTransformBase')->int:
        """
        Adds a new image effect to the end of the collection.
        
        Args:
            base (ImageTransformBase): The image effect to add
        
        Returns:
            int: Index position where the effect was added
        """
        intPtrbase:c_void_p = base.Ptr

        GetDllLibPpt().ImageTransform_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ImageTransform_Add.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ImageTransform_Add,self.Ptr, intPtrbase)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for iterating through the collection.
        
        Returns:
            IEnumerator: Enumerator for the collection
        """
        GetDllLibPpt().ImageTransform_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransform_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransform_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    def get_Item(self ,index:int)->'ImageTransformBase':
        """
        Gets an effect from the collection by its index.
        
        Args:
            index (int): Zero-based index of the effect to retrieve
        
        Returns:
            ImageTransformBase: The effect at the specified index
        """
        
        GetDllLibPpt().ImageTransform_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ImageTransform_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransform_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ImageTransformBase(intPtr)
        return ret


    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide associated with this image effects collection.
        
        Returns:
            ActiveSlide: The parent slide object
        """
        GetDllLibPpt().ImageTransform_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransform_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransform_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation associated with this image effects collection.
        
        Returns:
            Presentation: The parent presentation object
        """
        GetDllLibPpt().ImageTransform_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransform_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransform_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


