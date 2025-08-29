from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationProperty (  CommonBehavior) :
    """
    Represents property effect behavior in animations.
    
    This class controls how property values change during animations.
    """
    @property

    def From(self)->str:
        """
        Gets the starting value of the animation.
        
        Returns:
            str: The starting value as a string.
        """
        GetDllLibPpt().AnimationProperty_get_From.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_From.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationProperty_get_From,self.Ptr))
        return ret


    @From.setter
    def From(self, value:str):
        """
        Sets the starting value of the animation.
        
        Args:
            value: The starting value as a string.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().AnimationProperty_set_From.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_From,self.Ptr,valuePtr)

    @property

    def To(self)->str:
        """
        Gets the ending value of the animation.
        
        Returns:
            str: The ending value as a string.
        """
        GetDllLibPpt().AnimationProperty_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_To.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationProperty_get_To,self.Ptr))
        return ret


    @To.setter
    def To(self, value:str):
        """
        Sets the ending value of the animation.
        
        Args:
            value: The ending value as a string.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().AnimationProperty_set_To.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_To,self.Ptr,valuePtr)

    @property

    def By(self)->str:
        """
        Gets the relative offset value for the animation.
        
        Returns:
            str: The relative offset value.
        """
        GetDllLibPpt().AnimationProperty_get_By.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_By.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationProperty_get_By,self.Ptr))
        return ret


    @By.setter
    def By(self, value:str):
        """
        Sets the relative offset value for the animation.
        
        Args:
            value: The relative offset value.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().AnimationProperty_set_By.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_By,self.Ptr,valuePtr)

    @property

    def ValueType(self)->'PropertyValueType':
        """
        Gets the type of the property value.
        
        Returns:
            PropertyValueType: The type of the property value.
        """
        GetDllLibPpt().AnimationProperty_get_ValueType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_ValueType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationProperty_get_ValueType,self.Ptr)
        objwraped = PropertyValueType(ret)
        return objwraped

    @ValueType.setter
    def ValueType(self, value:'PropertyValueType'):
        """
        Sets the type of the property value.
        
        Args:
            value: The type to set.
        """
        GetDllLibPpt().AnimationProperty_set_ValueType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_ValueType,self.Ptr, value.value)

    @property
    def CalcMode(self)->'AnimationCalculationMode':
        """
        Gets the calculation mode for the animation.
        
        Returns:
            AnimationCalculationMode: The calculation mode.
        """
        GetDllLibPpt().AnimationProperty_get_CalcMode.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_CalcMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationProperty_get_CalcMode,self.Ptr)
        objwraped = AnimationCalculationMode(ret)
        return objwraped

    @CalcMode.setter
    def CalcMode(self, value:'AnimationCalculationMode'):
        """
        Sets the calculation mode for the animation.
        
        Args:
            value: The calculation mode to set.
        """
        GetDllLibPpt().AnimationProperty_set_CalcMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_CalcMode,self.Ptr, value.value)

    @property

    def TimeAnimationValueCollection(self)->'TimeAnimationValueCollection':
        """
        Gets the collection of time animation values.
        
        Returns:
            TimeAnimationValueCollection: The collection of animation values.
        """
        GetDllLibPpt().AnimationProperty_get_TimeAnimationValueCollection.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_TimeAnimationValueCollection.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationProperty_get_TimeAnimationValueCollection,self.Ptr)
        ret = None if intPtr==None else TimeAnimationValueCollection(intPtr)
        return ret


    @TimeAnimationValueCollection.setter
    def TimeAnimationValueCollection(self, value:'TimeAnimationValueCollection'):
        """
        Sets the collection of time animation values.
        
        Args:
            value: The collection to set.
        """
        GetDllLibPpt().AnimationProperty_set_TimeAnimationValueCollection.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_TimeAnimationValueCollection,self.Ptr, value.Ptr)

