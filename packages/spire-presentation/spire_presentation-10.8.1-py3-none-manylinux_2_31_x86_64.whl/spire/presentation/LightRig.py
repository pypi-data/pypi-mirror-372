from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LightRig (SpireObject) :
    """
    Represents a lighting configuration for 3D objects.

    This class defines how light sources are arranged to illuminate 3D shapes in presentations,
    including light direction, preset configurations, and rotation settings.
    """
    @property
    def Direction(self)->'LightingDirectionType':
        """
        Gets or sets the primary direction of the light source.

        Returns:
            LightingDirectionType: Current light direction
        """
        GetDllLibPpt().LightRig_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().LightRig_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LightRig_get_Direction,self.Ptr)
        objwraped = LightingDirectionType(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'LightingDirectionType'):
        """
        Sets the primary direction of the light source.

        Args:
            value: New lighting direction to apply
        """
        GetDllLibPpt().LightRig_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LightRig_set_Direction,self.Ptr, value.value)

    @property

    def PresetType(self)->'PresetLightRigType':
        """
        Gets or sets the predefined lighting configuration type.

        Returns:
            PresetLightRigType: Current preset light configuration
        """
        GetDllLibPpt().LightRig_get_PresetType.argtypes=[c_void_p]
        GetDllLibPpt().LightRig_get_PresetType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LightRig_get_PresetType,self.Ptr)
        objwraped = PresetLightRigType(ret)
        return objwraped

    @PresetType.setter
    def PresetType(self, value:'PresetLightRigType'):
        """
        Sets the predefined lighting configuration type.

        Args:
            value: New preset light configuration to apply
        """
        GetDllLibPpt().LightRig_set_PresetType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LightRig_set_PresetType,self.Ptr, value.value)


    def SetRotation(self ,latitude:float,longitude:float,revolution:float):
        """
        Defines the 3D rotation of the light rig using spherical coordinates.

        Args:
            latitude: Vertical angle in degrees (0-90)
            longitude: Horizontal angle in degrees (0-360)
            revolution: Rotation around the central axis in degrees (0-360)
        """
        
        GetDllLibPpt().LightRig_SetRotation.argtypes=[c_void_p ,c_float,c_float,c_float]
        CallCFunction(GetDllLibPpt().LightRig_SetRotation,self.Ptr, latitude,longitude,revolution)


    def GetRotation(self)->List[float]:
        """
        Retrieves the current 3D rotation coordinates of the light rig.

        Returns:
            List[float]: Array containing [latitude, longitude, revolution] values
        """
        GetDllLibPpt().LightRig_GetRotation.argtypes=[c_void_p]
        GetDllLibPpt().LightRig_GetRotation.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().LightRig_GetRotation,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this light rig is equivalent to another object.

        Args:
            obj: The object to compare with

        Returns:
            bool: True if the objects represent the same light configuration
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LightRig_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LightRig_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LightRig_Equals,self.Ptr, intPtrobj)
        return ret

