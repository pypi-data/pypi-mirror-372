from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EmbedImageList ( SpireObject ) :
    """
    Manages a collection of embedded images within a presentation.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of images in the collection.
        """
        GetDllLibPpt().EmbedImageList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().EmbedImageList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().EmbedImageList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        """
        Indexer to get the image element at specified position.
        Args:
            index: Zero-based position index.
        Returns:
            IImageData object at specified position.
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().EmbedImageList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().EmbedImageList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret

    def get_Item(self ,index:int)->'IImageData':
        """
        Gets the image element at specified position.
        Args:
            index: Zero-based position index.
        Returns:
            IImageData object at specified position.
    
        """
        
        GetDllLibPpt().EmbedImageList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().EmbedImageList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret

    def AppendImageData(self ,embedImage:IImageData)->IImageData:
        """
        Adds a copy of an image from another presentation.
        Args:
            embedImage: Source image data to copy.
        Returns:
            Added IImageData object.
        """
        intPtrembedImage:c_void_p = embedImage.Ptr

        GetDllLibPpt().EmbedImageList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EmbedImageList_Append.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_Append,self.Ptr, intPtrembedImage)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret


    #@dispatch

    #def Append(self ,image:'Stream')->IImageData:
    #    """
    #<summary>
    #    Add an image to a presentation.
    #</summary>
    #<param name="image">Image to add.</param>
    #<returns>Added image.</returns>
    #    """
    #    intPtrimage:c_void_p = image.Ptr

    #    GetDllLibPpt().EmbedImageList_AppendI.argtypes=[c_void_p ,c_void_p]
    #    GetDllLibPpt().EmbedImageList_AppendI.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_AppendI,self.Ptr, intPtrimage)
    #    ret = None if intPtr==None else IImageData(intPtr)
    #    return ret

    def AppendStream(self ,stream:'Stream')->'IImageData':
        """
        Adds an image to the presentation from a stream.
        Args:
            stream: Input stream containing image data.
        Returns:
            Added IImageData object.
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().EmbedImageList_AppendS.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EmbedImageList_AppendS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_AppendS,self.Ptr, intPtrstream)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for iterating through the collection.
        Returns:
            IEnumerator object for the entire collection.
        """
        GetDllLibPpt().EmbedImageList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().EmbedImageList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


