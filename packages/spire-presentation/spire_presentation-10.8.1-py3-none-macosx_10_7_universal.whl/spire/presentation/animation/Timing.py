from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Timing (  PptObject) :
    """
    Represents the timing properties for animation effects in a presentation.
    """
    @property
    def Accelerate(self)->float:
        """
        Gets or sets the acceleration percentage of the animation duration.
        
        Value range: 0.0 to 1.0 (0% to 100%)
        
        Returns:
            float: Acceleration percentage of animation duration
        """
        GetDllLibPpt().Timing_get_Accelerate.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Accelerate.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_Accelerate,self.Ptr)
        return ret

    @Accelerate.setter
    def Accelerate(self, value:float):
        GetDllLibPpt().Timing_set_Accelerate.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_Accelerate,self.Ptr, value)

    @property
    def Decelerate(self)->float:
        """
        Gets or sets the deceleration percentage of the animation duration.
        
        Value range: 0.0 to 1.0 (0% to 100%)
        
        Returns:
            float: Deceleration percentage of animation duration
        """
        GetDllLibPpt().Timing_get_Decelerate.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Decelerate.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_Decelerate,self.Ptr)
        return ret

    @Decelerate.setter
    def Decelerate(self, value:float):
        GetDllLibPpt().Timing_set_Decelerate.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_Decelerate,self.Ptr, value)

    @property
    def AutoReverse(self)->bool:
        """
        Gets or sets whether the animation automatically reverses after completion.
        
        Returns:
            bool: True if auto-reverse is enabled, False otherwise
        """
        GetDllLibPpt().Timing_get_AutoReverse.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_AutoReverse.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Timing_get_AutoReverse,self.Ptr)
        return ret

    @AutoReverse.setter
    def AutoReverse(self, value:bool):
        GetDllLibPpt().Timing_set_AutoReverse.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Timing_set_AutoReverse,self.Ptr, value)

    @property
    def Duration(self)->float:
        """
        Gets or sets the length of the animation in seconds.
        
        Returns:
            float: Animation duration in seconds
        """
        GetDllLibPpt().Timing_get_Duration.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Duration.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_Duration,self.Ptr)
        return ret

    @Duration.setter
    def Duration(self, value:float):
        GetDllLibPpt().Timing_set_Duration.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_Duration,self.Ptr, value)

    @property
    def RepeatCount(self)->float:
        """
        Gets or sets the number of times the animation should repeat.
        
        Special values:
            - 0: No repeat
            - 1: Play once (default)
            - n: Repeat n times
            - -1: Loop indefinitely until interrupted
        
        Returns:
            float: Animation repeat count
        """
        GetDllLibPpt().Timing_get_RepeatCount.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_RepeatCount.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_RepeatCount,self.Ptr)
        return ret

    @RepeatCount.setter
    def RepeatCount(self, value:float):
        GetDllLibPpt().Timing_set_RepeatCount.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_RepeatCount,self.Ptr, value)

    @property
    def RepeatDuration(self)->float:
        """
        Gets or sets the total duration for all animation repetitions in seconds.
       
        Returns:
            float: Total duration for all repetitions in seconds
        """
        GetDllLibPpt().Timing_get_RepeatDuration.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_RepeatDuration.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_RepeatDuration,self.Ptr)
        return ret

    @RepeatDuration.setter
    def RepeatDuration(self, value:float):
        GetDllLibPpt().Timing_set_RepeatDuration.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_RepeatDuration,self.Ptr, value)

    @property

    def Restart(self)->'AnimationRestartType':
        """
        Gets or sets the restart behavior of the animation.
        
        Returns:
            AnimationRestartType: Restart behavior enumeration
        """
        GetDllLibPpt().Timing_get_Restart.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Restart.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Timing_get_Restart,self.Ptr)
        objwraped = AnimationRestartType(ret)
        return objwraped

    @Restart.setter
    def Restart(self, value:'AnimationRestartType'):
        GetDllLibPpt().Timing_set_Restart.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Timing_set_Restart,self.Ptr, value.value)

    @property
    def Speed(self)->float:
        """
        Gets or sets the playback speed multiplier for the animation.
        
        Values:
            - 1.0: Normal speed (100%)
            - 2.0: Double speed (200%)
            - 0.5: Half speed (50%)
        
        Returns:
            float: Playback speed multiplier
        """
        GetDllLibPpt().Timing_get_Speed.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Speed.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_Speed,self.Ptr)
        return ret

    @Speed.setter
    def Speed(self, value:float):
        GetDllLibPpt().Timing_set_Speed.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_Speed,self.Ptr, value)

    @property
    def TriggerDelayTime(self)->float:
        """
        Gets or sets the delay time after trigger activation before animation starts.
        
        Returns:
            float: Trigger delay time in seconds
        """
        GetDllLibPpt().Timing_get_TriggerDelayTime.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_TriggerDelayTime.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_TriggerDelayTime,self.Ptr)
        return ret

    @TriggerDelayTime.setter
    def TriggerDelayTime(self, value:float):
        GetDllLibPpt().Timing_set_TriggerDelayTime.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_TriggerDelayTime,self.Ptr, value)

    @property

    def TriggerType(self)->'AnimationTriggerType':
        """
        Gets or sets the condition that triggers the animation.
        
        Returns:
            AnimationTriggerType: Animation trigger condition enumeration
        """
        GetDllLibPpt().Timing_get_TriggerType.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_TriggerType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Timing_get_TriggerType,self.Ptr)
        objwraped = AnimationTriggerType(ret)
        return objwraped

    @TriggerType.setter
    def TriggerType(self, value:'AnimationTriggerType'):
        GetDllLibPpt().Timing_set_TriggerType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Timing_set_TriggerType,self.Ptr, value.value)

    @property

    def AnimationRepeatType(self)->'AnimationRepeatType':
        """
        Gets or sets the repeat behavior type for the animation.
        
        Returns:
            AnimationRepeatType: Animation repeat behavior enumeration
        """
        GetDllLibPpt().Timing_get_AnimationRepeatType.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_AnimationRepeatType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Timing_get_AnimationRepeatType,self.Ptr)
        objwraped = AnimationRepeatType(ret)
        return objwraped

    @AnimationRepeatType.setter
    def AnimationRepeatType(self, value:'AnimationRepeatType'):
        GetDllLibPpt().Timing_set_AnimationRepeatType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Timing_set_AnimationRepeatType,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current timing settings.
        
        Args:
            obj (SpireObject): The object to compare with the current timing
            
        Returns:
            bool: True if the specified object has identical timing properties, otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Timing_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Timing_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Timing_Equals,self.Ptr, intPtrobj)
        return ret

