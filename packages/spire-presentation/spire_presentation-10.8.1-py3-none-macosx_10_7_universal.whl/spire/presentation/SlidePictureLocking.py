from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlidePictureLocking (  SimpleShapeBaseLocking) :
    """
    Indicates which operations are disabled on the parent PictureFrame.

    Properties:
        CropProtection: Indicates whether image cropping is forbidden.
    """
    @property
    def CropProtection(self)->bool:
        """
        Get whether image cropping is forbidden.

        Returns:
            bool: True if cropping is forbidden, False otherwise.
        """
        GetDllLibPpt().SlidePictureLocking_get_CropProtection.argtypes=[c_void_p]
        GetDllLibPpt().SlidePictureLocking_get_CropProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlidePictureLocking_get_CropProtection,self.Ptr)
        return ret

    @CropProtection.setter
    def CropProtection(self, value:bool):
        """
        Set whether image cropping is forbidden.

        Args:
            value: True to forbid cropping, False to allow it.
        """
        GetDllLibPpt().SlidePictureLocking_set_CropProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SlidePictureLocking_set_CropProtection,self.Ptr, value)

