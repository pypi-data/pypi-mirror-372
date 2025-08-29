from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideShowTransition (SpireObject) :
    """
    Represents slide show transition effects for a presentation slide.

    This class handles various aspects of slide transitions including sound effects, 
    timing, speed, and visual transition types.
    """

    @property

    def SoundMode(self)->'TransitionSoundMode':
        """
        Gets or sets the sound mode for the slide transition.

        Returns:
            TransitionSoundMode: The current sound mode setting.
        """
        GetDllLibPpt().SlideShowTransition_get_SoundMode.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_SoundMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_SoundMode,self.Ptr)
        objwraped = TransitionSoundMode(ret)
        return objwraped

    @SoundMode.setter
    def SoundMode(self, value:'TransitionSoundMode'):
        GetDllLibPpt().SlideShowTransition_set_SoundMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_SoundMode,self.Ptr, value.value)

    @property
    def BuiltInSound(self)->bool:
        """
        Indicates whether the transition sound is a built-in sound.

        Returns:
            bool: True if using a built-in sound, False otherwise.
        """
        GetDllLibPpt().SlideShowTransition_get_BuiltInSound.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_BuiltInSound.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_BuiltInSound,self.Ptr)
        return ret

    @BuiltInSound.setter
    def BuiltInSound(self, value:bool):
        GetDllLibPpt().SlideShowTransition_set_BuiltInSound.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_BuiltInSound,self.Ptr, value)

    @property
    def Loop(self)->bool:
        """
        Determines if the sound loops until next sound event.

        Returns:
            bool: True if sound should loop, False otherwise.
        """
        GetDllLibPpt().SlideShowTransition_get_Loop.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Loop.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Loop,self.Ptr)
        return ret

    @Loop.setter
    def Loop(self, value:bool):
        GetDllLibPpt().SlideShowTransition_set_Loop.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Loop,self.Ptr, value)

    @property
    def AdvanceOnClick(self)->bool:
        """
        Determines if mouse click advances the slide.

        Returns:
            bool: True if click advances slide, False otherwise.
        """
        GetDllLibPpt().SlideShowTransition_get_AdvanceOnClick.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_AdvanceOnClick.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_AdvanceOnClick,self.Ptr)
        return ret

    @AdvanceOnClick.setter
    def AdvanceOnClick(self, value:bool):
        GetDllLibPpt().SlideShowTransition_set_AdvanceOnClick.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_AdvanceOnClick,self.Ptr, value)

    @property

    def AdvanceAfterTime(self)->'int':
        """
        Gets auto-advance time in milliseconds.

        Returns:
            int: Time delay before auto-advancing (0 = no auto-advance).
        """
        GetDllLibPpt().SlideShowTransition_get_AdvanceAfterTime.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_AdvanceAfterTime.restype=c_void_p
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_AdvanceAfterTime,self.Ptr)
        return ret


    @AdvanceAfterTime.setter
    def AdvanceAfterTime(self, value:'int'):
        GetDllLibPpt().SlideShowTransition_set_AdvanceAfterTime.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_AdvanceAfterTime,self.Ptr, value)

    @property

    def Speed(self)->'TransitionSpeed':
        """
        Gets transition speed setting.

        Returns:
            TransitionSpeed: Current transition speed.
        """
        GetDllLibPpt().SlideShowTransition_get_Speed.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Speed.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Speed,self.Ptr)
        objwraped = TransitionSpeed(ret)
        return objwraped

    @Speed.setter
    def Speed(self, value:'TransitionSpeed'):
        GetDllLibPpt().SlideShowTransition_set_Speed.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Speed,self.Ptr, value.value)

    @property

    def Duration(self)->'int':
        """
        Gets transition duration in milliseconds.

        Returns:
            int: Duration of transition effect.
        """
        GetDllLibPpt().SlideShowTransition_get_Duration.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Duration.restype=c_void_p
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Duration,self.Ptr)
        return ret


    @Duration.setter
    def Duration(self, value:'int'):
        GetDllLibPpt().SlideShowTransition_set_Duration.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Duration,self.Ptr, value)

    @property

    def Value(self)->'Transition':
        """
        Gets the concrete transition object.

        Returns:
            Transition: Specific transition effect instance.
        """
        GetDllLibPpt().SlideShowTransition_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Value.restype=IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Value,self.Ptr)
        ret = None if intPtrWithTypeName==None else self.CreateTransition(intPtrWithTypeName)
        return ret

    @staticmethod
    def CreateTransition(intPtrWithTypeName:IntPtrWithTypeName)->'Transition':
        ret = None
        if intPtrWithTypeName == None :
            return ret
        intPtr = intPtrWithTypeName.intPtr[0] + (intPtrWithTypeName.intPtr[1]<<32)
        strName = PtrToStr(intPtrWithTypeName.typeName)
        if(strName == 'Spire.Presentation.Drawing.Transition.BlindsSlideTransition'):
            ret = BlindsSlideTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.FlythroughTransition'):
            ret = FlythroughTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.GlitterTransition'):
            ret = GlitterTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.InvXTransition'):
            ret = InvXTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.LRTransition'):
            ret = LRTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.OptionalBlackTransition'):
            ret = OptionalBlackTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.RevealTransition'):
            ret = RevealTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.ShredTransition'):
            ret = ShredTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.SideDirectionTransition'):
            ret = SideDirectionTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.SplitSlideTransition'):
            ret = SplitSlideTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.StripsSlideTransition'):
            ret = StripsSlideTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.WheelSlideTransition'):
            ret = WheelSlideTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.ZoomSlideTransition'):
            ret = ZoomSlideTransition(intPtr)
        else:
            ret = Transition(intPtr)

        return ret

    @property

    def Type(self)->'TransitionType':
        """
        Gets or sets the transition type.

        Returns:
            TransitionType: Current transition effect type.
        """
        GetDllLibPpt().SlideShowTransition_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Type,self.Ptr)
        objwraped = TransitionType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'TransitionType'):
        GetDllLibPpt().SlideShowTransition_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Type,self.Ptr, value.value)

    @property

    def Option(self)->'SpireObject':
        """
        Gets transition options object.

        Returns:
            SpireObject: Additional transition configuration options.
        """
        GetDllLibPpt().SlideShowTransition_get_Option.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Option.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Option,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Option.setter
    def Option(self, value:'SpireObject'):
        GetDllLibPpt().SlideShowTransition_set_Option.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Option,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Compares this transition with another object.

        Args:
            obj (SpireObject): Object to compare with.

        Returns:
            bool: True if objects are equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SlideShowTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideShowTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_Equals,self.Ptr, intPtrobj)
        return ret

