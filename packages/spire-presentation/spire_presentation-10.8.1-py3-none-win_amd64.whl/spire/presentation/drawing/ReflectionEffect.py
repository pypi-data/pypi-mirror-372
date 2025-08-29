from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ReflectionEffect (SpireObject) :
    """
    Represents a reflection effect that can be applied to visual elements.
    
    This class provides configurable properties to control the appearance of reflections,
    including position, opacity, blur, alignment, and transformation parameters.
    """

    #def MakeReflection(self ,bitmap:'Bitmap',reflectionEffect:'ReflectionEffect')->'Bitmap':
    #    """

    #    """
    #    intPtrbitmap:c_void_p = bitmap.Ptr
    #    intPtrreflectionEffect:c_void_p = reflectionEffect.Ptr

    #    GetDllLibPpt().ReflectionEffect_MakeReflection.argtypes=[c_void_p ,c_void_p,c_void_p]
    #    GetDllLibPpt().ReflectionEffect_MakeReflection.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().ReflectionEffect_MakeReflection,self.Ptr, intPtrbitmap,intPtrreflectionEffect)
    #    ret = None if intPtr==None else Bitmap(intPtr)
    #    return ret


    @property
    def StartPosition(self)->float:
        """
        Specifies the start position along the alpha gradient ramp for the reflection effect.
        
        Returns:
            float: The start position as a percentage value (0-100).
        """
        GetDllLibPpt().ReflectionEffect_get_StartPosition.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_StartPosition.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_StartPosition,self.Ptr)
        return ret

    @StartPosition.setter
    def StartPosition(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_StartPosition.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_StartPosition,self.Ptr, value)

    @property
    def EndPosition(self)->float:
        """
        Sets the start position along the alpha gradient ramp.
        
        Args:
            value: The start position percentage (0-100) to set.
        """
        GetDllLibPpt().ReflectionEffect_get_EndPosition.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_EndPosition.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_EndPosition,self.Ptr)
        return ret

    @EndPosition.setter
    def EndPosition(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_EndPosition.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_EndPosition,self.Ptr, value)

    @property
    def FadeDirection(self)->float:
        """
        Gets or sets the direction to offset the reflection.
        
        Returns:
            float: Fade direction angle in degrees.
        """
        GetDllLibPpt().ReflectionEffect_get_FadeDirection.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_FadeDirection.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_FadeDirection,self.Ptr)
        return ret

    @FadeDirection.setter
    def FadeDirection(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_FadeDirection.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_FadeDirection,self.Ptr, value)

    @property
    def StartOpacity(self)->float:
        """
        Gets or sets the starting opacity of the reflection.
        Returns:
            float: Starting opacity as a percentage value.
        """
        GetDllLibPpt().ReflectionEffect_get_StartOpacity.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_StartOpacity.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_StartOpacity,self.Ptr)
        return ret

    @StartOpacity.setter
    def StartOpacity(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_StartOpacity.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_StartOpacity,self.Ptr, value)

    @property
    def EndOpacity(self)->float:
        """
        Gets or sets the ending opacity of the reflection.
        
        Returns:
            float: Ending opacity as a percentage value.
        """
        GetDllLibPpt().ReflectionEffect_get_EndOpacity.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_EndOpacity.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_EndOpacity,self.Ptr)
        return ret

    @EndOpacity.setter
    def EndOpacity(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_EndOpacity.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_EndOpacity,self.Ptr, value)

    @property
    def BlurRadius(self)->float:
        """
        Gets or sets the blur radius of the reflection.
        
        Returns:
            float: Blur radius value.
        """
        GetDllLibPpt().ReflectionEffect_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_BlurRadius,self.Ptr)
        return ret

    @BlurRadius.setter
    def BlurRadius(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_BlurRadius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_BlurRadius,self.Ptr, value)

    @property
    def Direction(self)->float:
        """
        Gets or sets the direction of the reflection.
        
        Returns:
            float: Reflection direction angle in degrees.
        """
        GetDllLibPpt().ReflectionEffect_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_Direction,self.Ptr)
        return ret

    @Direction.setter
    def Direction(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_Direction.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_Direction,self.Ptr, value)

    @property
    def Distance(self)->float:
        """
        Gets or sets the distance of the reflection.
        
        Returns:
            float: Reflection distance value.
        """
        GetDllLibPpt().ReflectionEffect_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_Distance,self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_Distance.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_Distance,self.Ptr, value)

    @property

    def Alignment(self)->'RectangleAlignment':
        """
        Gets or sets the rectangle alignment of the reflection.
        
        Returns:
            RectangleAlignment: The alignment setting for the reflection.
        """
        GetDllLibPpt().ReflectionEffect_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_Alignment,self.Ptr)
        objwraped = RectangleAlignment(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'RectangleAlignment'):
        GetDllLibPpt().ReflectionEffect_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_Alignment,self.Ptr, value.value)

    @property
    def HorizontalSkew(self)->float:
        """
        Gets or sets the horizontal skew angle.
        
        Returns:
            float: Horizontal skew angle in degrees.
        """
        GetDllLibPpt().ReflectionEffect_get_HorizontalSkew.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_HorizontalSkew.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_HorizontalSkew,self.Ptr)
        return ret

    @HorizontalSkew.setter
    def HorizontalSkew(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_HorizontalSkew.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_HorizontalSkew,self.Ptr, value)

    @property
    def VerticalSkew(self)->float:
        """
        Gets or sets the vertical skew angle.
       
        Returns:
            float: Vertical skew angle in degrees.
        """
        GetDllLibPpt().ReflectionEffect_get_VerticalSkew.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_VerticalSkew.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_VerticalSkew,self.Ptr)
        return ret

    @VerticalSkew.setter
    def VerticalSkew(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_VerticalSkew.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_VerticalSkew,self.Ptr, value)

    @property
    def RotateWithShape(self)->bool:
        """
        Gets or sets whether the reflection rotates with the shape.
        
        Returns:
            bool: True if reflection rotates with shape, False otherwise.
        """
        GetDllLibPpt().ReflectionEffect_get_RotateWithShape.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_RotateWithShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_RotateWithShape,self.Ptr)
        return ret

    @RotateWithShape.setter
    def RotateWithShape(self, value:bool):
        GetDllLibPpt().ReflectionEffect_set_RotateWithShape.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_RotateWithShape,self.Ptr, value)

    @property
    def HorizontalScale(self)->float:
        """
        Gets or sets the horizontal scaling factor.
       
        Returns:
            float: Horizontal scale as a percentage value.
        """
        GetDllLibPpt().ReflectionEffect_get_HorizontalScale.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_HorizontalScale.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_HorizontalScale,self.Ptr)
        return ret

    @HorizontalScale.setter
    def HorizontalScale(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_HorizontalScale.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_HorizontalScale,self.Ptr, value)

    @property
    def VerticalScale(self)->float:
        """
        Gets or sets the vertical scaling factor.
        
        Returns:
            float: Vertical scale as a percentage value.
        """
        GetDllLibPpt().ReflectionEffect_get_VerticalScale.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionEffect_get_VerticalScale.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_get_VerticalScale,self.Ptr)
        return ret

    @VerticalScale.setter
    def VerticalScale(self, value:float):
        GetDllLibPpt().ReflectionEffect_set_VerticalScale.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ReflectionEffect_set_VerticalScale,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if the current ReflectionEffect is equal to another object.

        Args:
            obj: The object to compare with the current object

        Returns:
            bool: True if the specified object is equal to the current object; otherwise, False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ReflectionEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ReflectionEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ReflectionEffect_Equals,self.Ptr, intPtrobj)
        return ret

