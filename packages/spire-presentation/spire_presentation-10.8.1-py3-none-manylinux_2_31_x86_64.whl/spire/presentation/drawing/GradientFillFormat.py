from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientFillFormat (  IActiveSlide) :
    """
    Represents a gradient fill format applied to presentation shapes.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Checks if this GradientFillFormat equals another object.
        Args:
            obj: Object to compare.
        Returns:
            True if objects are equal; otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GradientFillFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GradientFillFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """

        """
        GetDllLibPpt().GradientFillFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_GetHashCode,self.Ptr)
        return ret

    @property

    def TileFlip(self)->'TileFlipMode':
        """
        Gets/sets the flipping mode for gradient tiling.
        """
        GetDllLibPpt().GradientFillFormat_get_TileFlip.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_TileFlip.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_get_TileFlip,self.Ptr)
        objwraped = TileFlipMode(ret)
        return objwraped

    @TileFlip.setter
    def TileFlip(self, value:'TileFlipMode'):
        GetDllLibPpt().GradientFillFormat_set_TileFlip.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GradientFillFormat_set_TileFlip,self.Ptr, value.value)

    @property

    def TileRectangle(self)->'RelativeRectangle':
        """
        Gets/sets the positioning rectangle for gradient tiling.
        """
        GetDllLibPpt().GradientFillFormat_get_TileRectangle.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_TileRectangle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientFillFormat_get_TileRectangle,self.Ptr)
        ret = None if intPtr==None else RelativeRectangle(intPtr)
        return ret


    @TileRectangle.setter
    def TileRectangle(self, value:'RelativeRectangle'):
        GetDllLibPpt().GradientFillFormat_set_TileRectangle.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().GradientFillFormat_set_TileRectangle,self.Ptr, value.Ptr)

    @property

    def GradientStyle(self)->'GradientStyle':
        """
        Gets/sets the orientation style of the gradient.
        """
        GetDllLibPpt().GradientFillFormat_get_GradientStyle.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_GradientStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_get_GradientStyle,self.Ptr)
        objwraped = GradientStyle(ret)
        return objwraped

    @GradientStyle.setter
    def GradientStyle(self, value:'GradientStyle'):
        GetDllLibPpt().GradientFillFormat_set_GradientStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GradientFillFormat_set_GradientStyle,self.Ptr, value.value)

    @property

    def GradientShape(self)->'GradientShapeType':
        """
        Gets/sets the geometric shape of the gradient.
        """
        GetDllLibPpt().GradientFillFormat_get_GradientShape.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_GradientShape.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_get_GradientShape,self.Ptr)
        objwraped = GradientShapeType(ret)
        return objwraped

    @GradientShape.setter
    def GradientShape(self, value:'GradientShapeType'):
        GetDllLibPpt().GradientFillFormat_set_GradientShape.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GradientFillFormat_set_GradientShape,self.Ptr, value.value)

    @property

    def GradientStops(self)->'GradientStopCollection':
        """
        Gets the collection of gradient color stops (read-only).
        """
        GetDllLibPpt().GradientFillFormat_get_GradientStops.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_GradientStops.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientFillFormat_get_GradientStops,self.Ptr)
        ret = None if intPtr==None else GradientStopCollection(intPtr)
        return ret


    @property

    def LinearGradientFill(self)->'LinearGradientFill':
        """
        Gets linear gradient properties (read-only).
        """
        GetDllLibPpt().GradientFillFormat_get_LinearGradientFill.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_LinearGradientFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientFillFormat_get_LinearGradientFill,self.Ptr)
        ret = None if intPtr==None else LinearGradientFill(intPtr)
        return ret


