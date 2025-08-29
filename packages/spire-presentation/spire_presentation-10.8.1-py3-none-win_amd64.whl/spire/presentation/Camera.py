from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Camera (SpireObject) :
    """
    Represents a 3D camera in a presentation scene.
    Controls the viewing perspective for 3D objects and scenes.
    """
    @property

    def PresetType(self)->'PresetCameraType':
        """
        Gets or sets the predefined camera type/preset.
        
        Returns:
            PresetCameraType: The current camera preset configuration.
        """
        GetDllLibPpt().Camera_get_PresetType.argtypes=[c_void_p]
        GetDllLibPpt().Camera_get_PresetType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Camera_get_PresetType,self.Ptr)
        objwraped = PresetCameraType(ret)
        return objwraped

    @PresetType.setter
    def PresetType(self, value:'PresetCameraType'):
        """
        Sets the predefined camera type/preset.
        
        Args:
            value (PresetCameraType): The new camera preset to apply.
        """
        GetDllLibPpt().Camera_set_PresetType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Camera_set_PresetType,self.Ptr, value.value)

    @property
    def FieldOfView(self)->float:
        """
        Gets or sets the camera's field of view angle in degrees.
        
        Returns:
            float: The current field of view angle.
        """
        GetDllLibPpt().Camera_get_FieldOfView.argtypes=[c_void_p]
        GetDllLibPpt().Camera_get_FieldOfView.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Camera_get_FieldOfView,self.Ptr)
        return ret

    @FieldOfView.setter
    def FieldOfView(self, value:float):
        GetDllLibPpt().Camera_set_FieldOfView.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Camera_set_FieldOfView,self.Ptr, value)

    @property
    def Zoom(self)->float:
        """
        Gets or sets the camera zoom percentage.
        
        Returns:
            float: The current zoom percentage.
        """
        GetDllLibPpt().Camera_get_Zoom.argtypes=[c_void_p]
        GetDllLibPpt().Camera_get_Zoom.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Camera_get_Zoom,self.Ptr)
        return ret

    @Zoom.setter
    def Zoom(self, value:float):
        """
        Sets the camera zoom percentage.
        
        Args:
            value (float): The new zoom percentage value.
        """
        GetDllLibPpt().Camera_set_Zoom.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Camera_set_Zoom,self.Ptr, value)


    def SetCameraRotation(self ,latitude:float,longitude:float,revolution:float):
        """
        Defines the camera rotation using three rotation angles.
        
        Args:
            latitude (float): Vertical rotation angle (up/down tilt)
            longitude (float): Horizontal rotation angle (left/right pan)
            revolution (float): Rotation around the view axis (twist)
        """
        GetDllLibPpt().Camera_SetCameraRotation.argtypes=[c_void_p ,c_float,c_float,c_float]
        CallCFunction(GetDllLibPpt().Camera_SetCameraRotation,self.Ptr, latitude,longitude,revolution)


    def GetCameraRotations(self)->List[float]:
        """
        Gets the current camera rotation angles.
        
        Returns:
            List[float]: [latitude, longitude, revolution] angles as a list.
            Returns None if no rotation is defined.
        """
        GetDllLibPpt().Camera_GetCameraRotations.argtypes=[c_void_p]
        GetDllLibPpt().Camera_GetCameraRotations.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Camera_GetCameraRotations,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this camera is equal to another object.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if objects are equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Camera_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Camera_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Camera_Equals,self.Ptr, intPtrobj)
        return ret

