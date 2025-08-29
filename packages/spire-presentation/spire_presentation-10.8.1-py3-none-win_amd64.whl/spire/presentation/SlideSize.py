from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideSize (SpireObject) :
    """
    Manages dimensions and orientation of presentation slides.

    This class handles both the physical size and display characteristics
    of slides in various measurement units and orientations.
    """
    @property

    def Size(self)->'SizeF':
        """
        Gets or sets slide dimensions in points.

        Returns:
            SizeF: Current size in points.
        """
        GetDllLibPpt().SlideSize_get_Size.argtypes=[c_void_p]
        GetDllLibPpt().SlideSize_get_Size.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideSize_get_Size,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @Size.setter
    def Size(self, value:'SizeF'):
        """
        Sets slide dimensions in points.

        Args:
            value (SizeF): New size in points.
        """
        GetDllLibPpt().SlideSize_set_Size.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideSize_set_Size,self.Ptr, value.Ptr)

    @property

    def SizeOfPx(self)->'SizeF':
        """
        Gets or sets slide dimensions in pixels.

        Returns:
            SizeF: Current size in pixels.
        """
        GetDllLibPpt().SlideSize_get_SizeOfPx.argtypes=[c_void_p]
        GetDllLibPpt().SlideSize_get_SizeOfPx.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideSize_get_SizeOfPx,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @SizeOfPx.setter
    def SizeOfPx(self, value:'SizeF'):
        """
        Sets slide dimensions in pixels.

        Args:
            value (SizeF): New size in pixels.
        """
        GetDllLibPpt().SlideSize_set_SizeOfPx.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideSize_set_SizeOfPx,self.Ptr, value.Ptr)

    @property

    def Type(self)->'SlideSizeType':
        """
        Gets or sets the size classification type.

        Returns:
            SlideSizeType: Standard size category.
        """
        GetDllLibPpt().SlideSize_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().SlideSize_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideSize_get_Type,self.Ptr)
        objwraped = SlideSizeType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'SlideSizeType'):
        """
        Sets the size classification type.

        Args:
            value (SlideSizeType): New size category.
        """
        GetDllLibPpt().SlideSize_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideSize_set_Type,self.Ptr, value.value)

    @property

    def Orientation(self)->'SlideOrienation':
        """
        Gets or sets the slide orientation.

        Returns:
            SlideOrienation: Current orientation (Landscape/Portrait).
        """
        GetDllLibPpt().SlideSize_get_Orientation.argtypes=[c_void_p]
        GetDllLibPpt().SlideSize_get_Orientation.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideSize_get_Orientation,self.Ptr)
        objwraped = SlideOrienation(ret)
        return objwraped

    @Orientation.setter
    def Orientation(self, value:'SlideOrienation'):
        """
        Sets the slide orientation.

        Args:
            value (SlideOrienation): New orientation to apply.
        """
        GetDllLibPpt().SlideSize_set_Orientation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideSize_set_Orientation,self.Ptr, value.value)

