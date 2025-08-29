from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlendEffect ( IActiveSlide ) :
    """
    Represents a blur effect applied to an entire shape including its fill.
    Affects all color channels including alpha.
    """
    @property
    def Radius(self)->float:
        """Gets or sets the blur radius."""
        GetDllLibPpt().BlendEffect_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().BlendEffect_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().BlendEffect_get_Radius,self.Ptr)
        return ret

    @Radius.setter
    def Radius(self, value:float):
        GetDllLibPpt().BlendEffect_set_Radius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().BlendEffect_set_Radius,self.Ptr, value)

    @property
    def IsGrow(self)->bool:
        """
        Indicates whether object bounds should grow due to blurring.
        True: bounds grow, False: maintain original bounds.
        """
        GetDllLibPpt().BlendEffect_get_IsGrow.argtypes=[c_void_p]
        GetDllLibPpt().BlendEffect_get_IsGrow.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().BlendEffect_get_IsGrow,self.Ptr)
        return ret

    @IsGrow.setter
    def IsGrow(self, value:bool):
        GetDllLibPpt().BlendEffect_set_IsGrow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().BlendEffect_set_IsGrow,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Indicates whether two BlendEffect instances are equal.

        Args:
            obj: The BlendEffect to compare with the current Tabs

        Returns:
            bool: True if the specified Tabs is equal to the current BlendEffect, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().BlendEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().BlendEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().BlendEffect_Equals,self.Ptr, intPtrobj)
        return ret

