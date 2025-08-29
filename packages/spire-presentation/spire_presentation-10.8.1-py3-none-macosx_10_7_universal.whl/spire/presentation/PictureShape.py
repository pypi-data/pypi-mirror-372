from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
from spire.presentation.drawing.IImageData import IImageData

class PictureShape (  IActiveSlide) :
    """
    Represents a picture in a presentation.
    """
    @property

    def EmbedImage(self)->'IImageData':
        """
        Gets or sets the embedded image.
        
        Returns:
            IImageData: The embedded image data.
        """
        GetDllLibPpt().PictureShape_get_EmbedImage.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_EmbedImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureShape_get_EmbedImage,self.Ptr)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret


    @EmbedImage.setter
    def EmbedImage(self, value:'IImageData'):
        """
        Sets the embedded image.
        
        Args:
            value (IImageData): The image data to set.
        """
        GetDllLibPpt().PictureShape_set_EmbedImage.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().PictureShape_set_EmbedImage,self.Ptr, value.Ptr)

    @property

    def Url(self)->str:
        """
        Gets or sets the URL of a linked image.
        
        Returns:
            str: The URL string of the linked image.
        """
        GetDllLibPpt().PictureShape_get_Url.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_Url.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().PictureShape_get_Url,self.Ptr))
        return ret


    @Url.setter
    def Url(self, value:str):
        """
        Sets the URL of a linked image.
        
        Args:
            value (str): The URL string to set.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().PictureShape_set_Url.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().PictureShape_set_Url,self.Ptr,valuePtr)

    @property
    def Transparency(self)->int:
        """
        Gets or sets the transparency level of the picture fill.
        
        Note: Value ranges from 0 (opaque) to 100 (fully transparent).
        
        Returns:
            int: The current transparency value.
        """
        GetDllLibPpt().PictureShape_get_Transparency.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_Transparency.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PictureShape_get_Transparency,self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:int):
        """
        Sets the transparency level of the picture fill.
        
        Args:
            value (int): Transparency value (0-100 range).
        """
        GetDllLibPpt().PictureShape_set_Transparency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().PictureShape_set_Transparency,self.Ptr, value)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide containing this picture.
        
        Returns:
            ActiveSlide: The parent slide object.
        """
        GetDllLibPpt().PictureShape_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureShape_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation containing this picture.
        
        Returns:
            Presentation: The parent presentation object.
        """
        GetDllLibPpt().PictureShape_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureShape_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


