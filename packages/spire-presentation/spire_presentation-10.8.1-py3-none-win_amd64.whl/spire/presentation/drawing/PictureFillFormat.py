from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PictureFillFormat (  IActiveSlide) :
    """
    <Represents the fill formatting properties for a picture.
    """
    @property
    def Dpi(self)->int:
        """
        Gets or sets the DPI resolution used for rendering the picture fill.
        
        Returns:
            int: The current DPI setting.
        """
        GetDllLibPpt().PictureFillFormat_get_Dpi.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_Dpi.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PictureFillFormat_get_Dpi,self.Ptr)
        return ret

    @Dpi.setter
    def Dpi(self, value:int):
        GetDllLibPpt().PictureFillFormat_set_Dpi.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_Dpi,self.Ptr, value)

    @property

    def FillType(self)->'PictureFillType':
        """
        Gets or sets the picture fill mode (tiled or stretched).
        
        Returns:
            PictureFillType: The current fill type.
        """
        GetDllLibPpt().PictureFillFormat_get_FillType.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PictureFillFormat_get_FillType,self.Ptr)
        objwraped = PictureFillType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'PictureFillType'):
        GetDllLibPpt().PictureFillFormat_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_FillType,self.Ptr, value.value)

    @property

    def Picture(self)->'PictureShape':
        """
        Gets the source picture used for filling.
        
        Returns:
            PictureShape: The source picture object.
        """
        GetDllLibPpt().PictureFillFormat_get_Picture.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_Picture.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureFillFormat_get_Picture,self.Ptr)
        ret = None if intPtr==None else PictureShape(intPtr)
        return ret


    @property

    def FillRectangle(self)->'RelativeRectangle':
        """
        Gets the dimensions of the fill area as relative coordinates.
        
        Returns:
            RelativeRectangle: The fill rectangle dimensions.
        """
        GetDllLibPpt().PictureFillFormat_get_FillRectangle.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_FillRectangle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureFillFormat_get_FillRectangle,self.Ptr)
        ret = None if intPtr==None else RelativeRectangle(intPtr)
        return ret


    @property
    def HorizontalOffset(self)->float:
        """
        Gets or sets the horizontal offset of the fill.
        
        Returns:
            float: The current horizontal offset.
        """
        GetDllLibPpt().PictureFillFormat_get_HorizontalOffset.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_HorizontalOffset.restype=c_double
        ret = CallCFunction(GetDllLibPpt().PictureFillFormat_get_HorizontalOffset,self.Ptr)
        return ret

    @HorizontalOffset.setter
    def HorizontalOffset(self, value:float):
        GetDllLibPpt().PictureFillFormat_set_HorizontalOffset.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_HorizontalOffset,self.Ptr, value)

    @property
    def VerticalOffset(self)->float:
        """
        Gets the cropping position of the picture.
        
        Returns:
            RectangleF: The crop rectangle in physical coordinates.
        """
        GetDllLibPpt().PictureFillFormat_get_VerticalOffset.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_VerticalOffset.restype=c_double
        ret = CallCFunction(GetDllLibPpt().PictureFillFormat_get_VerticalOffset,self.Ptr)
        return ret

    @VerticalOffset.setter
    def VerticalOffset(self, value:float):
        GetDllLibPpt().PictureFillFormat_set_VerticalOffset.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_VerticalOffset,self.Ptr, value)

    @property
    def ScaleX(self)->float:
        """
        Gets the cropping position of the picture.
        
        Returns:
            RectangleF: The crop rectangle in physical coordinates.
        """
        GetDllLibPpt().PictureFillFormat_get_ScaleX.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_ScaleX.restype=c_float
        ret = CallCFunction(GetDllLibPpt().PictureFillFormat_get_ScaleX,self.Ptr)
        return ret

    @ScaleX.setter
    def ScaleX(self, value:float):
        GetDllLibPpt().PictureFillFormat_set_ScaleX.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_ScaleX,self.Ptr, value)

    @property
    def ScaleY(self)->float:
        """
        Gets or sets the vertical scale factor.
        """
        GetDllLibPpt().PictureFillFormat_get_ScaleY.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_ScaleY.restype=c_float
        ret = CallCFunction(GetDllLibPpt().PictureFillFormat_get_ScaleY,self.Ptr)
        return ret

    @ScaleY.setter
    def ScaleY(self, value:float):
        GetDllLibPpt().PictureFillFormat_set_ScaleY.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_ScaleY,self.Ptr, value)

    @property

    def Flip(self)->'TileFlipMode':
        """
        Gets or sets the tile flip mode.
        """
        GetDllLibPpt().PictureFillFormat_get_Flip.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_Flip.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PictureFillFormat_get_Flip,self.Ptr)
        objwraped = TileFlipMode(ret)
        return objwraped

    @Flip.setter
    def Flip(self, value:'TileFlipMode'):
        GetDllLibPpt().PictureFillFormat_set_Flip.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_Flip,self.Ptr, value.value)

    @property

    def Alignment(self)->'RectangleAlignment':
        """
        Gets or sets the rectangle alignment.
        """
        GetDllLibPpt().PictureFillFormat_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PictureFillFormat_get_Alignment,self.Ptr)
        objwraped = RectangleAlignment(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'RectangleAlignment'):
        GetDllLibPpt().PictureFillFormat_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_Alignment,self.Ptr, value.value)

    @property

    def SourceRectangle(self)->'RelativeRectangle':
        """
        Gets or sets the number of percents of real image.
    
        """
        GetDllLibPpt().PictureFillFormat_get_SourceRectangle.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_SourceRectangle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureFillFormat_get_SourceRectangle,self.Ptr)
        ret = None if intPtr==None else RelativeRectangle(intPtr)
        return ret


    @SourceRectangle.setter
    def SourceRectangle(self, value:'RelativeRectangle'):
        GetDllLibPpt().PictureFillFormat_set_SourceRectangle.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().PictureFillFormat_set_SourceRectangle,self.Ptr, value.Ptr)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide (read-only).
        """
        GetDllLibPpt().PictureFillFormat_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureFillFormat_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation (read-only).
        """
        from spire.presentation import Presentation
        GetDllLibPpt().PictureFillFormat_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureFillFormat_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret



    def GetCropPosition(self)->'RectangleF':
        """
        Gets the crop position of picture format.
    
        """
        GetDllLibPpt().PictureFillFormat_GetCropPosition.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_GetCropPosition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureFillFormat_GetCropPosition,self.Ptr)
        ret = None if intPtr==None else RectangleF(intPtr)
        return ret



    def GetPicturePosition(self)->'RectangleF':
        """
        Gets the picture position of picture format.
    
        """
        GetDllLibPpt().PictureFillFormat_GetPicturePosition.argtypes=[c_void_p]
        GetDllLibPpt().PictureFillFormat_GetPicturePosition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureFillFormat_GetPicturePosition,self.Ptr)
        ret = None if intPtr==None else RectangleF(intPtr)
        return ret


