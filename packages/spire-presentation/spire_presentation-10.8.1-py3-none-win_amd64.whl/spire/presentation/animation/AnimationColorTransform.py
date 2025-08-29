from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationColorTransform (SpireObject) :
    """
    Represents color transformation parameters for animations.
    Defines color offset values used in animation effects.

    """
    @property
    def Color1(self)->float:
        """
        Gets or sets the first color component value.

        Returns:
            float: The first color component value.
        """
        GetDllLibPpt().AnimationColorTransform_get_Color1.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorTransform_get_Color1.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationColorTransform_get_Color1,self.Ptr)
        return ret

    @Color1.setter
    def Color1(self, value:float):
        """
        Sets the first color component value.

        Args:
            value: New value for the first color component.
        """
        GetDllLibPpt().AnimationColorTransform_set_Color1.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationColorTransform_set_Color1,self.Ptr, value)

    @property
    def Color2(self)->float:
        """
        Gets or sets the second color component value.

        Returns:
            float: The second color component value.
        """
        GetDllLibPpt().AnimationColorTransform_get_Color2.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorTransform_get_Color2.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationColorTransform_get_Color2,self.Ptr)
        return ret

    @Color2.setter
    def Color2(self, value:float):
        """
        Sets the second color component value.

        Args:
            value: New value for the second color component.
        """
        GetDllLibPpt().AnimationColorTransform_set_Color2.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationColorTransform_set_Color2,self.Ptr, value)

    @property
    def Color3(self)->float:
        """
        Gets or sets the third color component value.

        Returns:
            float: The third color component value.
        """
        GetDllLibPpt().AnimationColorTransform_get_Color3.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorTransform_get_Color3.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationColorTransform_get_Color3,self.Ptr)
        return ret

    @Color3.setter
    def Color3(self, value:float):
        """
        Sets the third color component value.

        Args:
            value: New value for the third color component.
        """
        GetDllLibPpt().AnimationColorTransform_set_Color3.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationColorTransform_set_Color3,self.Ptr, value)

