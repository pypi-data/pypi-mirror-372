from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeAnimationValue (  PptObject) :
    """
    Represents an animation point with time, value, and formula properties.
    """
    @property
    def Time(self)->float:
        """
        Gets or sets the time position in the animation sequence.
        
        Returns:
            float: Time value in seconds relative to animation start
        """
        GetDllLibPpt().TimeAnimationValue_get_Time.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValue_get_Time.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TimeAnimationValue_get_Time,self.Ptr)
        return ret

    @Time.setter
    def Time(self, value:float):
        GetDllLibPpt().TimeAnimationValue_set_Time.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TimeAnimationValue_set_Time,self.Ptr, value)

    @property

    def Value(self)->'SpireObject':
        """
        Gets or sets the animated property value at this time point.
        
        Returns:
            SpireObject: Can represent numeric, color, position or other animatable properties
        """
        GetDllLibPpt().TimeAnimationValue_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValue_get_Value.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeAnimationValue_get_Value,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Value.setter
    def Value(self, value:'SpireObject'):
        GetDllLibPpt().TimeAnimationValue_set_Value.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TimeAnimationValue_set_Value,self.Ptr, value.Ptr)

    @property

    def Formula(self)->str:
        """
        Gets or sets the formula expression for calculating animated values.
        Example: "sin(2*pi*t)" for sine wave animations.
        
        Returns:
            str: Mathematical expression defining value calculation
        """
        GetDllLibPpt().TimeAnimationValue_get_Formula.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValue_get_Formula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TimeAnimationValue_get_Formula,self.Ptr))
        return ret


    @Formula.setter
    def Formula(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TimeAnimationValue_set_Formula.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TimeAnimationValue_set_Formula,self.Ptr,valuePtr)

