from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillFormat (  IActiveSlide) :
    """
    Represents fill formatting options for presentation elements.
    """
    @property

    def FillType(self)->'FillFormatType':
        """
        Gets or sets the type of filling.
        
        Returns:
            FillFormatType: Current fill type
        """
        GetDllLibPpt().FillFormat_get_FillType.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillFormat_get_FillType,self.Ptr)
        objwraped = FillFormatType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'FillFormatType'):
        """
        Sets the fill type.
        
        Parameters:
            value (FillFormatType): New fill type
        """
        GetDllLibPpt().FillFormat_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().FillFormat_set_FillType,self.Ptr, value.value)

    @property
    def IsGroupFill(self)->bool:
        """
        Indicates whether this is a group fill.
        
        Returns:
            bool: True for group fill
        """
        GetDllLibPpt().FillFormat_get_IsGroupFill.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_IsGroupFill.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillFormat_get_IsGroupFill,self.Ptr)
        return ret

    @IsGroupFill.setter
    def IsGroupFill(self, value:bool):
        """
        Sets group fill status.
        
        Parameters:
            value (bool): New group fill status
        """
        GetDllLibPpt().FillFormat_set_IsGroupFill.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().FillFormat_set_IsGroupFill,self.Ptr, value)

    @property
    def IsNoFill(self)->bool:
        """
        Indicates whether no fill is applied.
        
        Returns:
            bool: True for no fill
        """
        GetDllLibPpt().FillFormat_get_IsNoFill.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_IsNoFill.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillFormat_get_IsNoFill,self.Ptr)
        return ret

    @property

    def SolidColor(self)->'ColorFormat':
        """
        Gets the solid fill color.
        
        Returns:
            ColorFormat: Color settings (read-only)
        """
        GetDllLibPpt().FillFormat_get_SolidColor.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_SolidColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormat_get_SolidColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Gradient(self)->'GradientFillFormat':
        """
        Gets the gradient fill settings.
        
        Returns:
            GradientFillFormat: Gradient settings (read-only)
        """
        GetDllLibPpt().FillFormat_get_Gradient.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_Gradient.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormat_get_Gradient,self.Ptr)
        ret = None if intPtr==None else GradientFillFormat(intPtr)
        return ret


    @property

    def Pattern(self)->'PatternFillFormat':
        """
        Gets the pattern fill settings.
        
        Returns:
            PatternFillFormat: Pattern settings (read-only)
        """
        GetDllLibPpt().FillFormat_get_Pattern.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_Pattern.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormat_get_Pattern,self.Ptr)
        ret = None if intPtr==None else PatternFillFormat(intPtr)
        return ret


    @property

    def PictureFill(self)->'PictureFillFormat':
        """
        Gets the picture fill settings.
        
        Returns:
            PictureFillFormat: Picture settings (read-only)
        """
        GetDllLibPpt().FillFormat_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormat_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    @property

    def RotateWithShape(self)->'TriState':
        """
        Gets or sets whether fill rotates with shape.
        
        Returns:
            TriState: Rotation behavior setting
        """
        GetDllLibPpt().FillFormat_get_RotateWithShape.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_RotateWithShape.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillFormat_get_RotateWithShape,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RotateWithShape.setter
    def RotateWithShape(self, value:'TriState'):
        """
        Sets rotation behavior.
        
        Parameters:
            value (TriState): New rotation behavior
        """
        GetDllLibPpt().FillFormat_set_RotateWithShape.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().FillFormat_set_RotateWithShape,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Checks equality with another FillFormat.
        
        Args:
            obj (SpireObject): FillFormat to compare
            
        Returns:
            bool: True if formats are equal
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillFormat_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
        Generates a hash code for this object.
        
        Returns:
            int: Hash code value
        """
        GetDllLibPpt().FillFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillFormat_GetHashCode,self.Ptr)
        return ret

