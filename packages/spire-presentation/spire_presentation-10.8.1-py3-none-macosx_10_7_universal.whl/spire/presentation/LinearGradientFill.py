from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LinearGradientFill (SpireObject) :
    """
    Represents a linear gradient fill for shapes and objects.
    """
    @property
    def Angle(self)->float:
        """
        Gets or sets the angle of a gradient.
        
        Args:
            value (float): The rotation angle in degrees (0-360 range)
        Returns:
            float: Current gradient angle
        """
        GetDllLibPpt().LinearGradientFill_get_Angle.argtypes=[c_void_p]
        GetDllLibPpt().LinearGradientFill_get_Angle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().LinearGradientFill_get_Angle,self.Ptr)
        return ret

    @Angle.setter
    def Angle(self, value:float):
        """
        Sets the rotation angle for the linear gradient.
        
        Args:
            value (float): Rotation angle in degrees (0-360 range)
        """
        GetDllLibPpt().LinearGradientFill_set_Angle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().LinearGradientFill_set_Angle,self.Ptr, value)

    @property

    def IsScaled(self)->'TriState':
        """
        Determines if gradient scaling is enabled relative to fill area.
        
        Returns:
            TriState: Current scaling state (True, False, or Inherit)
        """
        GetDllLibPpt().LinearGradientFill_get_IsScaled.argtypes=[c_void_p]
        GetDllLibPpt().LinearGradientFill_get_IsScaled.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LinearGradientFill_get_IsScaled,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsScaled.setter
    def IsScaled(self, value:'TriState'):
        """
        Enables or disables gradient scaling relative to fill area.
        
        Args:
            value (TriState): Scaling state to apply
        """
        GetDllLibPpt().LinearGradientFill_set_IsScaled.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LinearGradientFill_set_IsScaled,self.Ptr, value.value)

