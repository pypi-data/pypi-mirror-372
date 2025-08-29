from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ReflectionNode (  EffectNode) :
    """
    Represents a reflection effect node in a presentation effect chain.
   
    """
    @property
    def StartPosAlpha(self)->float:
        """
        Gets the start position along the alpha gradient ramp.
        
        Returns:
            float: Start position of alpha gradient as percentage (0-100%)
        """
        GetDllLibPpt().ReflectionNode_get_StartPosAlpha.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_StartPosAlpha.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_StartPosAlpha,self.Ptr)
        return ret

    @property
    def EndPosAlpha(self)->float:
        """
        Gets the end position along the alpha gradient ramp.
        
        Returns:
            float: End position of alpha gradient as percentage (0-100%)
        """
        GetDllLibPpt().ReflectionNode_get_EndPosAlpha.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_EndPosAlpha.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_EndPosAlpha,self.Ptr)
        return ret

    @property
    def FadeDirection(self)->float:
        """
        Gets the direction to offset the reflection.
        
        Returns:
            float: Reflection offset direction in degrees
        """
        GetDllLibPpt().ReflectionNode_get_FadeDirection.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_FadeDirection.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_FadeDirection,self.Ptr)
        return ret

    @property
    def StartReflectionOpacity(self)->float:
        """
        Gets the starting opacity of the reflection.
        
        Returns:
            float: Starting opacity as percentage (0-100%)
        """
        GetDllLibPpt().ReflectionNode_get_StartReflectionOpacity.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_StartReflectionOpacity.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_StartReflectionOpacity,self.Ptr)
        return ret

    @property
    def EndReflectionOpacity(self)->float:
        """
        Gets the ending opacity of the reflection.
        
        Returns:
            float: Ending opacity as percentage (0-100%)
        """
        GetDllLibPpt().ReflectionNode_get_EndReflectionOpacity.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_EndReflectionOpacity.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_EndReflectionOpacity,self.Ptr)
        return ret

    @property
    def BlurRadius(self)->float:
        """
        Gets the blur radius applied to the reflection.
        
        Returns:
            float: Blur radius value
        """
        GetDllLibPpt().ReflectionNode_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_BlurRadius,self.Ptr)
        return ret

    @property
    def Direction(self)->float:
        """
        Gets the direction of the reflection.
        
        Returns:
            float: Reflection direction in degrees
        """
        GetDllLibPpt().ReflectionNode_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_Direction,self.Ptr)
        return ret

    @property
    def Distance(self)->float:
        """
        Gets the distance offset of the reflection.
        
        Returns:
            float: Reflection distance offset
        """
        GetDllLibPpt().ReflectionNode_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_Distance,self.Ptr)
        return ret

    @property

    def RectangleAlign(self)->'RectangleAlignment':
        """
        Gets the rectangle alignment setting.
        
        Returns:
            RectangleAlignment: Alignment of the reflection rectangle
        """
        GetDllLibPpt().ReflectionNode_get_RectangleAlign.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_RectangleAlign.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_RectangleAlign,self.Ptr)
        objwraped = RectangleAlignment(ret)
        return objwraped

    @property
    def SkewH(self)->float:
        """
        Gets the horizontal skew angle.
        
        Returns:
            float: Horizontal skew angle in degrees
        """
        GetDllLibPpt().ReflectionNode_get_SkewH.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_SkewH.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_SkewH,self.Ptr)
        return ret

    @property
    def SkewV(self)->float:
        """
        Gets the vertical skew angle.
        
        Returns:
            float: Vertical skew angle in degrees
        """
        GetDllLibPpt().ReflectionNode_get_SkewV.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_SkewV.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_SkewV,self.Ptr)
        return ret

    @property
    def RotateShadowWithShape(self)->bool:
        """
        Determines if reflection rotates with the shape.
        
        Returns:
            bool: True if reflection rotates with shape, False otherwise
        """
        GetDllLibPpt().ReflectionNode_get_RotateShadowWithShape.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_RotateShadowWithShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_RotateShadowWithShape,self.Ptr)
        return ret

    @property
    def ScaleH(self)->float:
        """
        Gets the horizontal scaling factor.
        
        Returns:
            float: Horizontal scaling as percentage (negative values flip)
        """
        GetDllLibPpt().ReflectionNode_get_ScaleH.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_ScaleH.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_ScaleH,self.Ptr)
        return ret

    @property
    def ScaleV(self)->float:
        """
        Gets the vertical scaling factor.
        
        Returns:
            float: Vertical scaling as percentage (negative values flip)
        """
        GetDllLibPpt().ReflectionNode_get_ScaleV.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_ScaleV.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_ScaleV,self.Ptr)
        return ret

