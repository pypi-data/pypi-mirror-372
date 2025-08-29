from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationEffect (  PptObject) :
    """
    Represents timing information about a slide animation.
    
    This class controls the timing and behavior of animation effects.
    """
    @property

    def TimeNodeAudios(self)->List['TimeNodeAudio']:
        """
        Gets the collection of audio elements associated with the animation.
        
        Returns:
            List[TimeNodeAudio]: The list of audio elements.
        """
        GetDllLibPpt().AnimationEffect_get_TimeNodeAudios.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_TimeNodeAudios.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().AnimationEffect_get_TimeNodeAudios,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, TimeNodeAudio)
        return ret


    @property
    def IterateTimeValue(self)->float:
        """
        Gets the iteration interval value.
        
        Returns:
            float: The iteration interval value.
        """
        GetDllLibPpt().AnimationEffect_get_IterateTimeValue.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_IterateTimeValue.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_IterateTimeValue,self.Ptr)
        return ret

    @IterateTimeValue.setter
    def IterateTimeValue(self, value:float):
        """
        Sets the iteration interval value.
        
        Args:
            value: The iteration interval value to set.
        """
        GetDllLibPpt().AnimationEffect_set_IterateTimeValue.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_IterateTimeValue,self.Ptr, value)

    @property

    def IterateType(self)->'AnimateType':
        """
        Gets the iteration type.
        
        Returns:
            AnimateType: The iteration type.
        """
        GetDllLibPpt().AnimationEffect_get_IterateType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_IterateType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_IterateType,self.Ptr)
        objwraped = AnimateType(ret)
        return objwraped

    @IterateType.setter
    def IterateType(self, value:'AnimateType'):
        """
        Sets the iteration type.
        
        Args:
            value: The iteration type to set.
        """
        GetDllLibPpt().AnimationEffect_set_IterateType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_IterateType,self.Ptr, value.value)

    @property

    def Effects(self)->'AnimationEffectCollection':
        """
        Gets the sequence of effects.
        
        Returns:
            AnimationEffectCollection: The collection of effects.
        """
        GetDllLibPpt().AnimationEffect_get_Effects.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_Effects.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_Effects,self.Ptr)
        ret = None if intPtr==None else AnimationEffectCollection(intPtr)
        return ret


    @property

    def TextAnimation(self)->'TextAnimation':
        """
        Gets the text animation settings.
        
        Returns:
            TextAnimation: The text animation object.
        """
        GetDllLibPpt().AnimationEffect_get_TextAnimation.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_TextAnimation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_TextAnimation,self.Ptr)
        ret = None if intPtr==None else TextAnimation(intPtr)
        return ret


    @property

    def GraphicAnimation(self)->'GraphicAnimation':
        """
        Gets the graphic animation settings.
        
        Returns:
            GraphicAnimation: The graphic animation object.
        """
        GetDllLibPpt().AnimationEffect_get_GraphicAnimation.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_GraphicAnimation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_GraphicAnimation,self.Ptr)
        ret = None if intPtr==None else GraphicAnimation(intPtr)
        return ret


    @property

    def ShapeTarget(self)->'Shape':
        """
        Gets the shape that the animation is applied to.
        
        Returns:
            Shape: The target shape.
        """
        GetDllLibPpt().AnimationEffect_get_ShapeTarget.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_ShapeTarget.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_ShapeTarget,self.Ptr)
        ret = None if intPtr==None else Shape(intPtr)
        return ret


    @property

    def PresetClassType(self)->'TimeNodePresetClassType':
        """
        Gets the class type of the effect.
        
        Returns:
            TimeNodePresetClassType: The effect class type.
        """
        GetDllLibPpt().AnimationEffect_get_PresetClassType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_PresetClassType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_PresetClassType,self.Ptr)
        objwraped = TimeNodePresetClassType(ret)
        return objwraped

    @PresetClassType.setter
    def PresetClassType(self, value:'TimeNodePresetClassType'):
        """
        Sets the class type of the effect.
        
        Args:
            value: The effect class type to set.
        """
        GetDllLibPpt().AnimationEffect_set_PresetClassType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_PresetClassType,self.Ptr, value.value)

    @property

    def AnimationEffectType(self)->'AnimationEffectType':
        """
        Gets the type of animation effect.
        
        Returns:
            AnimationEffectType: The effect type.
        """
        GetDllLibPpt().AnimationEffect_get_AnimationEffectType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_AnimationEffectType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_AnimationEffectType,self.Ptr)
        objwraped = AnimationEffectType(ret)
        return objwraped

    @AnimationEffectType.setter
    def AnimationEffectType(self, value:'AnimationEffectType'):
        """
        Sets the type of animation effect.
        
        Args:
            value: The effect type to set.
        """
        GetDllLibPpt().AnimationEffect_set_AnimationEffectType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_AnimationEffectType,self.Ptr, value.value)

    @property

    def Subtype(self)->'AnimationEffectSubtype':
        """
        Gets the subtype of the animation effect.
        
        Returns:
            AnimationEffectSubtype: The effect subtype.
        """
        GetDllLibPpt().AnimationEffect_get_Subtype.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_Subtype.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_Subtype,self.Ptr)
        objwraped = AnimationEffectSubtype(ret)
        return objwraped

    @Subtype.setter
    def Subtype(self, value:'AnimationEffectSubtype'):
        """
        Sets the subtype of the animation effect.
        
        Args:
            value: The effect subtype to set.
        """
        GetDllLibPpt().AnimationEffect_set_Subtype.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_Subtype,self.Ptr, value.value)

    @property

    def CommonBehaviorCollection(self)->'CommonBehaviorCollection':
        """
        Gets the collection of behaviors for the effect.
        
        Returns:
            CommonBehaviorCollection: The behavior collection.
        """
        from spire.presentation.animation.CommonBehaviorCollection import CommonBehaviorCollection
        GetDllLibPpt().AnimationEffect_get_CommonBehaviorCollection.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_CommonBehaviorCollection.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_CommonBehaviorCollection,self.Ptr)
        ret = None if intPtr==None else CommonBehaviorCollection(intPtr)
        return ret


    @CommonBehaviorCollection.setter
    def CommonBehaviorCollection(self, value:'CommonBehaviorCollection'):
        """
        Sets the collection of behaviors for the effect.
        
        Args:
            value: The behavior collection to set.
        """
        GetDllLibPpt().AnimationEffect_set_CommonBehaviorCollection.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_CommonBehaviorCollection,self.Ptr, value.Ptr)

    @property

    def Timing(self)->'Timing':
        """
        Gets the timing settings for the effect.
        
        Returns:
            Timing: The timing settings.
        """
        from spire.presentation.animation.Timing import Timing;
        GetDllLibPpt().AnimationEffect_get_Timing.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_Timing.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_Timing,self.Ptr)
        ret = None if intPtr==None else Timing(intPtr)
        return ret


    @Timing.setter
    def Timing(self, value:'Timing'):
        """
        Sets the timing settings for the effect.
        
        Args:
            value: The timing settings to set.
        """
        GetDllLibPpt().AnimationEffect_set_Timing.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_Timing,self.Ptr, value.Ptr)

    @property

    def StartParagraph(self)->'TextParagraph':
        """
        Gets the starting text paragraph for the effect.
        
        Returns:
            TextParagraph: The starting paragraph.
        """
        GetDllLibPpt().AnimationEffect_get_StartParagraph.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_StartParagraph.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_StartParagraph,self.Ptr)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret


    @property

    def EndParagraph(self)->'TextParagraph':
        """
        Gets the ending text paragraph for the effect.
        
        Returns:
            TextParagraph: The ending paragraph.
        """
        GetDllLibPpt().AnimationEffect_get_EndParagraph.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_EndParagraph.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_EndParagraph,self.Ptr)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret



    def SetStartEndParagraphs(self ,startParaIndex:int,endParaIndex:int):
        """
        Sets the start and end paragraphs for the effect.
        
        Args:
            startParaIndex: Index of the starting paragraph.
            endParaIndex: Index of the ending paragraph.
        """
        
        GetDllLibPpt().AnimationEffect_SetStartEndParagraphs.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_SetStartEndParagraphs,self.Ptr, startParaIndex,endParaIndex)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this object is equal to another.
        
        Args:
            obj: The object to compare with.
            
        Returns:
            bool: True if equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().AnimationEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().AnimationEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_Equals,self.Ptr, intPtrobj)
        return ret

