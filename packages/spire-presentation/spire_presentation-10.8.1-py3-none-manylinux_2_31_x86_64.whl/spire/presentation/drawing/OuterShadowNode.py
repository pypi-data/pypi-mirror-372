from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OuterShadowNode (  EffectNode) :
    """
    Represents a outer shadow effect applied to presentation elements.
    Provides properties to control the visual appearance of the shadow.
    """
    @property
    def BlurRadius(self)->float:
        """
        Gets the blur radius of the shadow effect.
        A higher value creates a softer, more diffused shadow.

        Returns:
            float: Blur radius value.
        """
        GetDllLibPpt().OuterShadowNode_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_BlurRadius,self.Ptr)
        return ret

    @property
    def Direction(self)->float:
        """
        Gets the directional angle of the shadow effect.
        Measured in degrees (0-360) where 0 points directly to the right.

        Returns:
            float: Direction angle in degrees.
        """
        GetDllLibPpt().OuterShadowNode_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_Direction,self.Ptr)
        return ret

    @property
    def Distance(self)->float:
        """
        Gets the distance between the element and its shadow.
        Larger values create more separation between object and shadow.

        Returns:
            float: Shadow distance value.
        """
        GetDllLibPpt().OuterShadowNode_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_Distance,self.Ptr)
        return ret

    @property

    def ShadowColor(self)->'Color':
        """
        Gets the color of the shadow effect.

        Returns:
            Color: Color object representing shadow color.
        """
        GetDllLibPpt().OuterShadowNode_get_ShadowColor.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_ShadowColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OuterShadowNode_get_ShadowColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def RectangleAlign(self)->'RectangleAlignment':
        """
        Gets the rectangle alignment setting for the shadow.
        Determines how the shadow is positioned relative to the element.

        Returns:
            RectangleAlignment: Alignment setting enum value.
        """
        GetDllLibPpt().OuterShadowNode_get_RectangleAlign.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_RectangleAlign.restype=c_int
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_RectangleAlign,self.Ptr)
        objwraped = RectangleAlignment(ret)
        return objwraped

    @property
    def SkewHorizontal(self)->float:
        """
        Gets the horizontal skew angle of the shadow.
        Creates perspective distortion effect along X-axis.

        Returns:
            float: Horizontal skew angle.
        """
        GetDllLibPpt().OuterShadowNode_get_SkewHorizontal.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_SkewHorizontal.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_SkewHorizontal,self.Ptr)
        return ret

    @property
    def SkewVertical(self)->float:
        """
        Gets the vertical skew angle of the shadow.
        Creates perspective distortion effect along Y-axis.

        Returns:
            float: Vertical skew angle.
        """
    
        GetDllLibPpt().OuterShadowNode_get_SkewVertical.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_SkewVertical.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_SkewVertical,self.Ptr)
        return ret

    @property
    def RotateShadowWithShape(self)->bool:
        """
        Determines if shadow rotates with the element during transformations.

        Returns:
            bool: True if shadow rotates with shape, False otherwise.
        """
        GetDllLibPpt().OuterShadowNode_get_RotateShadowWithShape.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_RotateShadowWithShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_RotateShadowWithShape,self.Ptr)
        return ret

    @property
    def ScaleHorizontal(self)->float:
        """
        Gets the horizontal scaling factor of the shadow.
        Values < 1 compress, > 1 stretch, and negative values flip horizontally.

        Returns:
            float: Horizontal scaling factor.
        """
        GetDllLibPpt().OuterShadowNode_get_ScaleHorizontal.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_ScaleHorizontal.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_ScaleHorizontal,self.Ptr)
        return ret

    @property
    def ScaleVertical(self)->float:
        """
        Gets the vertical scaling factor of the shadow.
        Values < 1 compress, > 1 stretch, and negative values flip vertically.

        Returns:
            float: Vertical scaling factor.
        """
        GetDllLibPpt().OuterShadowNode_get_ScaleVertical.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_ScaleVertical.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_ScaleVertical,self.Ptr)
        return ret

