from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationColorBehavior (  CommonBehavior) :
    """
    Represents a color effect for an animation behavior.

    """
    @property

    def From(self)->'ColorFormat':
        """
        Gets the starting color of the behavior.
        
        Returns:
            ColorFormat: The starting color.
        """
        GetDllLibPpt().AnimationColorBehavior_get_From.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorBehavior_get_From.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationColorBehavior_get_From,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @From.setter
    def From(self, value:'ColorFormat'):
        """
        Sets the starting color of the behavior.
        
        Args:
            value: The starting color to set.
        """
        GetDllLibPpt().AnimationColorBehavior_set_From.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationColorBehavior_set_From,self.Ptr, value.Ptr)

    @property

    def To(self)->'ColorFormat':
        """
        Gets the ending color of the behavior.
        
        Returns:
            ColorFormat: The ending color.
        """
        GetDllLibPpt().AnimationColorBehavior_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorBehavior_get_To.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationColorBehavior_get_To,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @To.setter
    def To(self, value:'ColorFormat'):
        """
        Sets the ending color of the behavior.
        
        Args:
            value: The ending color to set.
        """
        GetDllLibPpt().AnimationColorBehavior_set_To.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationColorBehavior_set_To,self.Ptr, value.Ptr)

    @property

    def By(self)->'AnimationColorTransform':
        """
        Gets the relative color value for the animation.
        
        Returns:
            AnimationColorTransform: The relative color transformation.
        """
        GetDllLibPpt().AnimationColorBehavior_get_By.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorBehavior_get_By.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationColorBehavior_get_By,self.Ptr)
        ret = None if intPtr==None else AnimationColorTransform(intPtr)
        return ret


    @By.setter
    def By(self, value:'AnimationColorTransform'):
        """
        Sets the relative color value for the animation.
        
        Args:
            value: The relative color transformation to set.
        """
        GetDllLibPpt().AnimationColorBehavior_set_By.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationColorBehavior_set_By,self.Ptr, value.Ptr)

    @property

    def AnimationColorspace(self)->'AnimationColorspace':
        """
        Gets the color space used for the behavior.
        
        Returns:
            AnimationColorspace: The color space setting.
        """
        GetDllLibPpt().AnimationColorBehavior_get_AnimationColorspace.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorBehavior_get_AnimationColorspace.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationColorBehavior_get_AnimationColorspace,self.Ptr)
        objwraped = AnimationColorspace(ret)
        return objwraped

    @AnimationColorspace.setter
    def AnimationColorspace(self, value:'AnimationColorspace'):
        """
        Sets the color space used for the behavior.
        
        Args:
            value: The color space to set.
        """
        GetDllLibPpt().AnimationColorBehavior_set_AnimationColorspace.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationColorBehavior_set_AnimationColorspace,self.Ptr, value.value)

    @property

    def Direction(self)->'AnimationColorDirection':
        """
        Gets the direction to cycle the hue.
        
        Returns:
            AnimationColorDirection: The color direction.
        """
        GetDllLibPpt().AnimationColorBehavior_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorBehavior_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationColorBehavior_get_Direction,self.Ptr)
        objwraped = AnimationColorDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'AnimationColorDirection'):
        """
        Sets the direction to cycle the hue.
        
        Args:
            value: The color direction to set.
        """
        GetDllLibPpt().AnimationColorBehavior_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationColorBehavior_set_Direction,self.Ptr, value.value)

