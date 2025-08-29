from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PictureData (SpireObject) :
    """
    Represents an image in a presentation document.
    
    Provides access to embedded/linked image data and transformation effects.
    """
    @property

    def SourceEmbedImage(self)->'IImageData':
        """
        Gets or sets the embedded image data.
        
        Returns:
            IImageData: Embedded image object.
        """
        GetDllLibPpt().PictureData_get_SourceEmbedImage.argtypes=[c_void_p]
        GetDllLibPpt().PictureData_get_SourceEmbedImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureData_get_SourceEmbedImage,self.Ptr)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret


    @property

    def Url(self)->str:
        """
        Gets or sets the URL for linked images.
        
        Returns:
            str: URL string for externally linked images.
        """
        GetDllLibPpt().PictureData_get_Url.argtypes=[c_void_p]
        GetDllLibPpt().PictureData_get_Url.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().PictureData_get_Url,self.Ptr))
        return ret


    @property

    def ImageTransform(self)->'EffectDataCollection':
        """
        Gets the collection of image transformation effects.
        
        Returns:
            EffectDataCollection: Read-only collection of visual effects.
        """
        GetDllLibPpt().PictureData_get_ImageTransform.argtypes=[c_void_p]
        GetDllLibPpt().PictureData_get_ImageTransform.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureData_get_ImageTransform,self.Ptr)
        ret = None if intPtr==None else EffectDataCollection(intPtr)
        return ret


