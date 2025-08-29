from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FormatThreeD (  PptObject, IActiveSlide) :
    """
    Represents 3-D formatting properties for shapes or objects.
    Provides access to camera settings, lighting configuration, and 3D shape properties.
    """
    @property

    def Camera(self)->'Camera':
        """
        Gets or sets the camera settings for 3D rendering.
        Controls the viewpoint and perspective of the 3D object.
        """
        GetDllLibPpt().FormatThreeD_get_Camera.argtypes=[c_void_p]
        GetDllLibPpt().FormatThreeD_get_Camera.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatThreeD_get_Camera,self.Ptr)
        ret = None if intPtr==None else Camera(intPtr)
        return ret


    @Camera.setter
    def Camera(self, value:'Camera'):
        """
        Set the camera settings for 3D rendering.
        Args:
            value: Camera object defining viewpoint and perspective
        """
        GetDllLibPpt().FormatThreeD_set_Camera.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().FormatThreeD_set_Camera,self.Ptr, value.Ptr)

    @property

    def LightRig(self)->'LightRig':
        """
        Gets or sets the lighting configuration for 3D rendering.
        Defines light source properties and direction.
        """
        GetDllLibPpt().FormatThreeD_get_LightRig.argtypes=[c_void_p]
        GetDllLibPpt().FormatThreeD_get_LightRig.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatThreeD_get_LightRig,self.Ptr)
        ret = None if intPtr==None else LightRig(intPtr)
        return ret


    @LightRig.setter
    def LightRig(self, value:'LightRig'):
        """
        Set the lighting configuration for 3D rendering.
        Args:
            value: LightRig object defining lighting properties
        """
        GetDllLibPpt().FormatThreeD_set_LightRig.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().FormatThreeD_set_LightRig,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current object.
        Args:
            obj: The object to compare with the current object
        Returns:
            bool: True if objects are equal, otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FormatThreeD_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FormatThreeD_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FormatThreeD_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def ShapeThreeD(self)->'ShapeThreeD':
        """
        Gets the 3D shape properties including extrusion, contour, and material properties.
        
        """
        GetDllLibPpt().FormatThreeD_get_ShapeThreeD.argtypes=[c_void_p]
        GetDllLibPpt().FormatThreeD_get_ShapeThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatThreeD_get_ShapeThreeD,self.Ptr)
        ret = None if intPtr==None else ShapeThreeD(intPtr)
        return ret


