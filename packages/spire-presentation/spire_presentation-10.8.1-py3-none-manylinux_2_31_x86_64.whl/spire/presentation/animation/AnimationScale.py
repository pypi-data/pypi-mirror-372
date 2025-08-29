from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationScale (  CommonBehavior) :
    """
    Represents a scale animation effect.
    
    This class controls scaling animations.
    """
    @property

    def ZoomContent(self)->'TriState':
        """
        Indicates whether content should be zoomed during the animation.
        
        Returns:
            TriState: The zoom content setting.
        """
        GetDllLibPpt().AnimationScale_get_ZoomContent.argtypes=[c_void_p]
        GetDllLibPpt().AnimationScale_get_ZoomContent.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationScale_get_ZoomContent,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @ZoomContent.setter
    def ZoomContent(self, value:'TriState'):
        """
        Sets whether content should be zoomed during the animation.
        
        Args:
            value: The zoom content setting to set.
        """
        GetDllLibPpt().AnimationScale_set_ZoomContent.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationScale_set_ZoomContent,self.Ptr, value.value)

    @property

    def From(self)->'PointF':
        """
        Gets the starting scale value (in percentages).
        
        Returns:
            PointF: The starting scale value.
        """
        GetDllLibPpt().AnimationScale_get_From.argtypes=[c_void_p]
        GetDllLibPpt().AnimationScale_get_From.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationScale_get_From,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @From.setter
    def From(self, value:'PointF'):
        """
        Sets the starting scale value (in percentages).
        
        Args:
            value: The starting scale value to set.
        """
        GetDllLibPpt().AnimationScale_set_From.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationScale_set_From,self.Ptr, value.Ptr)

    @property

    def To(self)->'PointF':
        """
        Gets the ending location for the scale effect.
        
        Returns:
            PointF: The ending scale value.
        """
        GetDllLibPpt().AnimationScale_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationScale_get_To.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationScale_get_To,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @To.setter
    def To(self, value:'PointF'):
        """
        Sets the ending location for the scale effect.
        
        Args:
            value: The ending scale value to set.
        """
        GetDllLibPpt().AnimationScale_set_To.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationScale_set_To,self.Ptr, value.Ptr)

    @property

    def By(self)->'PointF':
        """
        Gets the relative offset value for the animation.
        
        Returns:
            PointF: The relative offset value.
        """
        GetDllLibPpt().AnimationScale_get_By.argtypes=[c_void_p]
        GetDllLibPpt().AnimationScale_get_By.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationScale_get_By,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @By.setter
    def By(self, value:'PointF'):
        """
        Sets the relative offset value for the animation.
        
        Args:
            value: The relative offset value to set.
        """
        GetDllLibPpt().AnimationScale_set_By.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationScale_set_By,self.Ptr, value.Ptr)

