from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationRotation (  CommonBehavior) :
    """
    Represents rotation behavior in animation effects.
    """
    @property
    def From(self)->float:
        """
        Gets or sets the starting rotation angle (in degrees).

        """
        GetDllLibPpt().AnimationRotation_get_From.argtypes=[c_void_p]
        GetDllLibPpt().AnimationRotation_get_From.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationRotation_get_From,self.Ptr)
        return ret

    @From.setter
    def From(self, value:float):
        GetDllLibPpt().AnimationRotation_set_From.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationRotation_set_From,self.Ptr, value)

    @property
    def To(self)->float:
        """
        Gets or sets the ending rotation angle (in degrees).

        """
        GetDllLibPpt().AnimationRotation_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationRotation_get_To.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationRotation_get_To,self.Ptr)
        return ret

    @To.setter
    def To(self, value:float):
        GetDllLibPpt().AnimationRotation_set_To.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationRotation_set_To,self.Ptr, value)

    @property
    def By(self)->float:
        """
        Gets or sets the relative rotation offset (in degrees).

        """
        GetDllLibPpt().AnimationRotation_get_By.argtypes=[c_void_p]
        GetDllLibPpt().AnimationRotation_get_By.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationRotation_get_By,self.Ptr)
        return ret

    @By.setter
    def By(self, value:float):
        GetDllLibPpt().AnimationRotation_set_By.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationRotation_set_By,self.Ptr, value)

