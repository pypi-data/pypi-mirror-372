from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlidePicture (  ShapeNode, IEmbedImage) :
    """
    Represents a picture in a slide.
    """
    @property

    def ShapeLocking(self)->'SlidePictureLocking':
        """
        Get the shape locking settings.

        Returns:
            SlidePictureLocking: The locking settings for the picture.
        """
        GetDllLibPpt().SlidePicture_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().SlidePicture_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlidePicture_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else SlidePictureLocking(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """
        Get the type of the shape.

        Returns:
            ShapeType: The current shape type.
        """
        GetDllLibPpt().SlidePicture_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().SlidePicture_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlidePicture_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        GetDllLibPpt().SlidePicture_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlidePicture_set_ShapeType,self.Ptr, value.value)

    @property
    def IsCropped(self)->bool:
        """
        Determine if the picture is cropped.

        Returns:
            bool: True if the picture is cropped, False otherwise.
        """
        GetDllLibPpt().SlidePicture_get_IsCropped.argtypes=[c_void_p]
        GetDllLibPpt().SlidePicture_get_IsCropped.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlidePicture_get_IsCropped,self.Ptr)
        return ret

    @property

    def PictureFill(self)->'PictureFillFormat':
        """
        Get the picture fill format.

        Returns:
            PictureFillFormat: The fill format of the picture.
        """
        GetDllLibPpt().SlidePicture_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().SlidePicture_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlidePicture_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    def PictureAdjust(self):
        """Adjust the picture of the slide."""
        GetDllLibPpt().SlidePicture_PictureAdjust.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().SlidePicture_PictureAdjust,self.Ptr)


    def Crop(self ,x:float,y:float,width:float,height:float):
        """
        Crop the picture of the slide.

        Args:
            x: The x-coordinate for cropping.
            y: The y-coordinate for cropping.
            width: The width of the cropped area.
            height: The height of the cropped area.
        """
        
        GetDllLibPpt().SlidePicture_Crop.argtypes=[c_void_p ,c_float,c_float,c_float,c_float]
        CallCFunction(GetDllLibPpt().SlidePicture_Crop,self.Ptr, x,y,width,height)

