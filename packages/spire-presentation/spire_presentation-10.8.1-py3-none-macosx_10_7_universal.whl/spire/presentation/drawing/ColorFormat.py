from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ColorFormat (  PptObject) :
    """Represents the color of a one-color object."""

    @property
    def Color(self)->'Color':
        """
        Gets or sets the RGB color value.

        Returns:
            Color: RGB color object.
        """
        GetDllLibPpt().ColorFormat_get_Color.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorFormat_get_Color,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        """
        Sets the RGB color value.

        Args:
            value (Color): RGB color to set.
        """
        GetDllLibPpt().ColorFormat_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Color,self.Ptr, value.Ptr)

    @property

    def ColorType(self)->'ColorType':
        """
        Gets or sets the color type.

        Returns:
            ColorType: Enum value representing color type.
        """
        GetDllLibPpt().ColorFormat_get_ColorType.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_ColorType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_ColorType,self.Ptr)
        objwraped = ColorType(ret)
        return objwraped

    @ColorType.setter
    def ColorType(self, value:'ColorType'):
        """
        Sets the color type.

        Args:
            value (ColorType): Enum value to set.
        """
        GetDllLibPpt().ColorFormat_set_ColorType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_ColorType,self.Ptr, value.value)

    @property

    def KnownColor(self)->'KnownColors':
        """
        Gets or sets the preset color.

        Returns:
            KnownColors: Enum value for preset color.
        """
        GetDllLibPpt().ColorFormat_get_KnownColor.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_KnownColor,self.Ptr)
        objwraped = KnownColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'KnownColors'):
        """
        Sets the preset color.

        Args:
            value (KnownColors): Enum value to set.
        """
        GetDllLibPpt().ColorFormat_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_KnownColor,self.Ptr, value.value)

    @property

    def SystemColor(self)->'SystemColorType':
        """
        Gets or sets system color table value.

        Returns:
            SystemColorType: Enum value for system color.
        """
        GetDllLibPpt().ColorFormat_get_SystemColor.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_SystemColor.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_SystemColor,self.Ptr)
        objwraped = SystemColorType(ret)
        return objwraped

    @SystemColor.setter
    def SystemColor(self, value:'SystemColorType'):
        """
        Sets system color table value.

        Args:
            value (SystemColorType): Enum value to set.
        """
        GetDllLibPpt().ColorFormat_set_SystemColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_SystemColor,self.Ptr, value.value)

    @property

    def SchemeColor(self)->'SchemeColor':
        """
        Gets or sets color scheme value.

        Returns:
            SchemeColor: Enum value in color scheme.
        """
        GetDllLibPpt().ColorFormat_get_SchemeColor.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_SchemeColor.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_SchemeColor,self.Ptr)
        objwraped = SchemeColor(ret)
        return objwraped

    @SchemeColor.setter
    def SchemeColor(self, value:'SchemeColor'):
        """
        Sets color scheme value.

        Args:
            value (SchemeColor): Enum value to set.
        """
        GetDllLibPpt().ColorFormat_set_SchemeColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_SchemeColor,self.Ptr, value.value)

    @property
    def R(self)->int:
        """
        Gets or sets the red component (0-255).

        Returns:
            int: Red component value.
        """

        GetDllLibPpt().ColorFormat_get_R.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_R.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_R,self.Ptr)
        return ret

    @R.setter
    def R(self, value:int):
        """
        Sets the red component.

        Args:
            value (int): Red value (0-255).
        """
        GetDllLibPpt().ColorFormat_set_R.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_R,self.Ptr, value)

    @property
    def G(self)->int:
        """
        Gets or sets the green component (0-255).

        Returns:
            int: Green component value.
        """
        GetDllLibPpt().ColorFormat_get_G.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_G.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_G,self.Ptr)
        return ret

    @G.setter
    def G(self, value:int):
        """
        Sets the green component.

        Args:
            value (int): Green value (0-255).
        """
        GetDllLibPpt().ColorFormat_set_G.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_G,self.Ptr, value)

    @property
    def B(self)->int:
        """
        Gets or sets the blue component (0-255).

        Returns:
            int: Blue component value.
        """
        GetDllLibPpt().ColorFormat_get_B.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_B.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_B,self.Ptr)
        return ret

    @B.setter
    def B(self, value:int):
        """
        Sets the blue component.

        Args:
            value (int): Blue value (0-255).
        """
        GetDllLibPpt().ColorFormat_set_B.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_B,self.Ptr, value)

    @property
    def Hue(self)->float:
        """
        Gets or sets the HSL hue component.

        Returns:
            float: Hue value (0-360).
        """
        GetDllLibPpt().ColorFormat_get_Hue.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Hue.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Hue,self.Ptr)
        return ret

    @Hue.setter
    def Hue(self, value:float):
        GetDllLibPpt().ColorFormat_set_Hue.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Hue,self.Ptr, value)

    @property
    def Saturation(self)->float:
        """
        Gets or sets the HSL saturation component.

        Returns:
            float: Saturation value (0-1).
        """
        GetDllLibPpt().ColorFormat_get_Saturation.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Saturation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Saturation,self.Ptr)
        return ret

    @Saturation.setter
    def Saturation(self, value:float):
        GetDllLibPpt().ColorFormat_set_Saturation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Saturation,self.Ptr, value)

    @property
    def Luminance(self)->float:
        """
        Gets or sets the HSL luminance component.

        Returns:
            float: Luminance value (0-1).
        """
        GetDllLibPpt().ColorFormat_get_Luminance.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Luminance.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Luminance,self.Ptr)
        return ret

    @Luminance.setter
    def Luminance(self, value:float):
        GetDllLibPpt().ColorFormat_set_Luminance.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Luminance,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if two colors are equal.

        Args:
            obj (SpireObject): Color to compare.

        Returns:
            bool: True if colors are equal.
        """

        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ColorFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ColorFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ColorFormat_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
        Gets hash code for the color.

        Returns:
            int: Hash code value.
        """
        GetDllLibPpt().ColorFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_GetHashCode,self.Ptr)
        return ret
    

    @property

    def Transparency(self)->'float':
        """
        Gets or sets transparency level (0-100%).

        Returns:
            float: Transparency value.
        """
        GetDllLibPpt().ColorFormat_get_Transparency.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Transparency.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Transparency,self.Ptr)
        return ret


    @Transparency.setter
    def Transparency(self, value:'float'):
        GetDllLibPpt().ColorFormat_set_Transparency.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Transparency,self.Ptr, value)


    @property

    def Brightness(self)->'float':
        """
        Gets or sets brightness adjustment (-100% to 100%).

        Returns:
            float: Brightness value.
        """
        GetDllLibPpt().ColorFormat_get_Brightness.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Brightness.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Brightness,self.Ptr)
        return ret


    @Brightness.setter
    def Brightness(self, value:'float'):
        GetDllLibPpt().ColorFormat_set_Brightness.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Brightness,self.Ptr, value)

