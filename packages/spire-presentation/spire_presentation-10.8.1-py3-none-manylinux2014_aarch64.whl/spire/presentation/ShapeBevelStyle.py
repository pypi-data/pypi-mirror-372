from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeBevelStyle (SpireObject) :
    """
    Contains properties defining 3D bevel effects for shapes.

    This class controls the three-dimensional bevel effects applied to shapes,
    including width, height, and style presets.
    """
    @property
    def Width(self)->float:
        """
        Get or set the bevel width.

        Returns:
            float: The current bevel width measurement.
        """
        GetDllLibPpt().ShapeBevelStyle_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ShapeBevelStyle_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeBevelStyle_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        """
        Set the bevel width.

        Args:
            value (float): The new width value to set.
        """
        GetDllLibPpt().ShapeBevelStyle_set_Width.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeBevelStyle_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Get or set the bevel height.

        Returns:
            float: The current bevel height measurement.
        """
        GetDllLibPpt().ShapeBevelStyle_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ShapeBevelStyle_get_Height.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeBevelStyle_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        """
        Set the bevel height.

        Args:
            value (float): The new height value to set.
        """
        GetDllLibPpt().ShapeBevelStyle_set_Height.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeBevelStyle_set_Height,self.Ptr, value)

    @property

    def PresetType(self)->'BevelPresetType':
        """
        Get or set the bevel style type.

        Returns:
            BevelPresetType: The current bevel style preset.
        """
        GetDllLibPpt().ShapeBevelStyle_get_PresetType.argtypes=[c_void_p]
        GetDllLibPpt().ShapeBevelStyle_get_PresetType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeBevelStyle_get_PresetType,self.Ptr)
        objwraped = BevelPresetType(ret)
        return objwraped

    @PresetType.setter
    def PresetType(self, value:'BevelPresetType'):
        """
        Set the bevel style type.

        Args:
            value (BevelPresetType): The new bevel preset type to apply.
        """
        GetDllLibPpt().ShapeBevelStyle_set_PresetType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeBevelStyle_set_PresetType,self.Ptr, value.value)

