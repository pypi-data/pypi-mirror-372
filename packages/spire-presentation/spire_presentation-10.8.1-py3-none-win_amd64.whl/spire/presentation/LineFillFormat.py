from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineFillFormat (  PptObject, IActiveSlide, IActivePresentation) :
    """
    Represents properties for filling lines with colors, gradients, or patterns.
    """
    @property

    def FillType(self)->'FillFormatType':
        """
        Gets or sets the fill type.

        Returns:
            FillFormatType: The current fill type.
        """
        GetDllLibPpt().LineFillFormat_get_FillType.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LineFillFormat_get_FillType,self.Ptr)
        objwraped = FillFormatType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'FillFormatType'):
        """
        Sets the fill type.

        Args:
            value (FillFormatType): The new fill type to set.
        """
        GetDllLibPpt().LineFillFormat_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LineFillFormat_set_FillType,self.Ptr, value.value)

    @property

    def SolidFillColor(self)->'ColorFormat':
        """
        Gets the color of a solid fill.

        Returns:
            ColorFormat: The solid fill color object.
        """
        GetDllLibPpt().LineFillFormat_get_SolidFillColor.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_SolidFillColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineFillFormat_get_SolidFillColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Gradient(self)->'GradientFillFormat':
        """
        Gets the gradient fill format.

        Returns:
            GradientFillFormat: The gradient fill object.
        """
        GetDllLibPpt().LineFillFormat_get_Gradient.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_Gradient.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineFillFormat_get_Gradient,self.Ptr)
        ret = None if intPtr==None else GradientFillFormat(intPtr)
        return ret


    @property

    def Pattern(self)->'PatternFillFormat':
        """
        Gets the pattern fill format.

        Returns:
            PatternFillFormat: The pattern fill object.
        """
        GetDllLibPpt().LineFillFormat_get_Pattern.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_Pattern.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineFillFormat_get_Pattern,self.Ptr)
        ret = None if intPtr==None else PatternFillFormat(intPtr)
        return ret


    @property

    def RotateWithShape(self)->'TriState':
        """
        Gets whether the fill rotates with the shape.

        Returns:
            TriState: Current rotation behavior setting.
        """
        GetDllLibPpt().LineFillFormat_get_RotateWithShape.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_RotateWithShape.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LineFillFormat_get_RotateWithShape,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RotateWithShape.setter
    def RotateWithShape(self, value:'TriState'):
        """
        Sets whether the fill should rotate with the shape.

        Args:
            value (TriState): New rotation behavior setting.
        """
        GetDllLibPpt().LineFillFormat_set_RotateWithShape.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LineFillFormat_set_RotateWithShape,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this object equals another object.

        Args:
            obj (SpireObject): The object to compare.

        Returns:
            bool: True if objects are equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LineFillFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LineFillFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LineFillFormat_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
        Generates a hash code for this object.

        Returns:
            int: The computed hash code.
        """
        GetDllLibPpt().LineFillFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LineFillFormat_GetHashCode,self.Ptr)
        return ret

