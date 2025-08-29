from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PatternFillFormat (  IActiveSlide, IActivePresentation) :
    """
    Represents a pattern to fill a shape.
    
    This class provides properties and methods to work with pattern fills, 
    including pattern type configuration and color settings for both foreground
    and background elements of the pattern.
    """
    @property

    def PatternType(self)->'PatternFillType':
        """Gets or sets the pattern style."""
        GetDllLibPpt().PatternFillFormat_get_PatternType.argtypes=[c_void_p]
        GetDllLibPpt().PatternFillFormat_get_PatternType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PatternFillFormat_get_PatternType,self.Ptr)
        objwraped = PatternFillType(ret)
        return objwraped

    @PatternType.setter
    def PatternType(self, value:'PatternFillType'):
        GetDllLibPpt().PatternFillFormat_set_PatternType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().PatternFillFormat_set_PatternType,self.Ptr, value.value)

    @property

    def ForegroundColor(self)->'ColorFormat':
        """
        Gets the foreground pattern color.
        """
        GetDllLibPpt().PatternFillFormat_get_ForegroundColor.argtypes=[c_void_p]
        GetDllLibPpt().PatternFillFormat_get_ForegroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PatternFillFormat_get_ForegroundColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def BackgroundColor(self)->'ColorFormat':
        """
        Gets the background pattern color.
        """
        GetDllLibPpt().PatternFillFormat_get_BackgroundColor.argtypes=[c_void_p]
        GetDllLibPpt().PatternFillFormat_get_BackgroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PatternFillFormat_get_BackgroundColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    #@dispatch

    #def GetTileImage(self ,background:Color,foreground:Color)->Bitmap:
    #    """
    #<summary>
    #    Creates a tile image for the pattern fill with a specified colors.
    #</summary>
    #<param name="background">The background <see cref="T:System.Drawing.Color" /> for the pattern.</param>
    #<param name="foreground">The foreground <see cref="T:System.Drawing.Color" /> for the pattern.</param>
    #<returns>Tile <see cref="T:System.Drawing.Bitmap" />.</returns>
    #    """
    #    intPtrbackground:c_void_p = background.Ptr
    #    intPtrforeground:c_void_p = foreground.Ptr

    #    GetDllLibPpt().PatternFillFormat_GetTileImage.argtypes=[c_void_p ,c_void_p,c_void_p]
    #    GetDllLibPpt().PatternFillFormat_GetTileImage.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().PatternFillFormat_GetTileImage,self.Ptr, intPtrbackground,intPtrforeground)
    #    ret = None if intPtr==None else Bitmap(intPtr)
    #    return ret


    #@dispatch

    #def GetTileImage(self ,styleColor:Color)->Bitmap:
    #    """
    #<summary>
    #    Creates a tile image for the pattern fill.
    #</summary>
    #<param name="styleColor">The default <see cref="T:System.Drawing.Color" />, defined in ShapeEx's Style object. Fill's colors can depend on this.</param>
    #<returns>Tile <see cref="T:System.Drawing.Bitmap" />.</returns>
    #    """
    #    intPtrstyleColor:c_void_p = styleColor.Ptr

    #    GetDllLibPpt().PatternFillFormat_GetTileImageS.argtypes=[c_void_p ,c_void_p]
    #    GetDllLibPpt().PatternFillFormat_GetTileImageS.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().PatternFillFormat_GetTileImageS,self.Ptr, intPtrstyleColor)
    #    ret = None if intPtr==None else Bitmap(intPtr)
    #    return ret


