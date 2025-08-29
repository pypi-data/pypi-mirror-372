from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GlowEffect (SpireObject) :
    """
    Represents a glow visual effect where a blurred color outline is added 
    outside the edges of an object.
    """

    @dispatch
    def __init__(self):
        """Initializes a new instance of the GlowEffect class."""
        GetDllLibPpt().GlowEffect_CreatGlowEffect.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GlowEffect_CreatGlowEffect)
        super(GlowEffect, self).__init__(intPtr)
    
    @property
    def Radius(self)->float:
        """
        Gets or sets the blur radius of the glow effect. Larger values create 
            more diffuse glows. Default is 0.0.
        """
        GetDllLibPpt().GlowEffect_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().GlowEffect_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().GlowEffect_get_Radius,self.Ptr)
        return ret

    @Radius.setter
    def Radius(self, value:float):
        GetDllLibPpt().GlowEffect_set_Radius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().GlowEffect_set_Radius,self.Ptr, value)

    @property

    def ColorFormat(self)->'ColorFormat':
        """
         Gets the color format used for the glow effect (read-only). Use 
            properties of the returned ColorFormat object to modify the glow color.
        """
        GetDllLibPpt().GlowEffect_get_ColorFormat.argtypes=[c_void_p]
        GetDllLibPpt().GlowEffect_get_ColorFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GlowEffect_get_ColorFormat,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this GlowEffect is equal to another object.
        Args:
            obj: The SpireObject to compare with this GlowEffect.
        Returns:
            True if the objects are equal; otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GlowEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GlowEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GlowEffect_Equals,self.Ptr, intPtrobj)
        return ret

