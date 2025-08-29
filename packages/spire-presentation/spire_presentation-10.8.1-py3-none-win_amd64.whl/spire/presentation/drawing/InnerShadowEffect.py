from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class InnerShadowEffect (SpireObject) :
    """
    Represents inner shadow effect properties for presentation elements.
    """

    @dispatch
    def __init__(self):
        GetDllLibPpt().InnerShadowEffect_CreatInnerShadowEffect.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().InnerShadowEffect_CreatInnerShadowEffect)
        super(InnerShadowEffect, self).__init__(intPtr)
   
    @property
    def BlurRadius(self)->float:
        """
        Gets or sets the blur radius of the shadow.
        """
        GetDllLibPpt().InnerShadowEffect_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowEffect_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().InnerShadowEffect_get_BlurRadius,self.Ptr)
        return ret

    @BlurRadius.setter
    def BlurRadius(self, value:float):
        GetDllLibPpt().InnerShadowEffect_set_BlurRadius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().InnerShadowEffect_set_BlurRadius,self.Ptr, value)

    @property
    def Direction(self)->float:
        """
        Gets or sets the direction angle of the shadow (in degrees).
        """
        GetDllLibPpt().InnerShadowEffect_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowEffect_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().InnerShadowEffect_get_Direction,self.Ptr)
        return ret

    @Direction.setter
    def Direction(self, value:float):
        GetDllLibPpt().InnerShadowEffect_set_Direction.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().InnerShadowEffect_set_Direction,self.Ptr, value)

    @property
    def Distance(self)->float:
        """
        Gets or sets the distance offset of the shadow.
        """
        GetDllLibPpt().InnerShadowEffect_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowEffect_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().InnerShadowEffect_get_Distance,self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:float):
        GetDllLibPpt().InnerShadowEffect_set_Distance.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().InnerShadowEffect_set_Distance,self.Ptr, value)

    @property

    def ColorFormat(self)->'ColorFormat':
        """
        Gets the color settings of the shadow.
        """
        GetDllLibPpt().InnerShadowEffect_get_ColorFormat.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowEffect_get_ColorFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().InnerShadowEffect_get_ColorFormat,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current InnerShadowEffect is equal to another InnerShadowEffect.
        
        Args:
            obj: (SpireObject): The InnerShadowEffect to compare with.
            
        Returns:
            bool: True if objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().InnerShadowEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().InnerShadowEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().InnerShadowEffect_Equals,self.Ptr, intPtrobj)
        return ret

