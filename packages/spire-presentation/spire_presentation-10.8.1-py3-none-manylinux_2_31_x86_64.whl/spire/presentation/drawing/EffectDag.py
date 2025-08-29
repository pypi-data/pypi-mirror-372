from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectDag (  PptObject, IActiveSlide, IActivePresentation) :
    """
    Represents effect properties of shape.
    
    This class provides access to various visual effects that can be applied to shapes.
    """
    @property

    def BlendEffect(self)->'BlendEffect':
        """
        Gets or sets the blend effect.
        
        Returns:
            BlendEffect: The blend effect object.
        """
        GetDllLibPpt().EffectDag_get_BlendEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_BlendEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_BlendEffect,self.Ptr)
        ret = None if intPtr==None else BlendEffect(intPtr)
        return ret


    @BlendEffect.setter
    def BlendEffect(self, value:'BlendEffect'):
        GetDllLibPpt().EffectDag_set_BlendEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_BlendEffect,self.Ptr, value.Ptr)

    @property

    def FillOverlayEffect(self)->'FillOverlayEffect':
        """
        Gets or sets the fill overlay effect.
        
        Returns:
            FillOverlayEffect: The fill overlay effect object.
        """
        GetDllLibPpt().EffectDag_get_FillOverlayEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_FillOverlayEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_FillOverlayEffect,self.Ptr)
        ret = None if intPtr==None else FillOverlayEffect(intPtr)
        return ret


    @FillOverlayEffect.setter
    def FillOverlayEffect(self, value:'FillOverlayEffect'):
        GetDllLibPpt().EffectDag_set_FillOverlayEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_FillOverlayEffect,self.Ptr, value.Ptr)

    @property

    def GlowEffect(self)->'GlowEffect':
        """
        Gets or sets the glow effect.
        
        Returns:
            GlowEffect: The glow effect object.
        """
        GetDllLibPpt().EffectDag_get_GlowEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_GlowEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_GlowEffect,self.Ptr)
        ret = None if intPtr==None else GlowEffect(intPtr)
        return ret


    @GlowEffect.setter
    def GlowEffect(self, value:'GlowEffect'):
        GetDllLibPpt().EffectDag_set_GlowEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_GlowEffect,self.Ptr, value.Ptr)

    @property

    def InnerShadowEffect(self)->'InnerShadowEffect':
        """
        Gets or sets the inner shadow effect.
        
        Returns:
            InnerShadowEffect: The inner shadow effect object.
        """
        GetDllLibPpt().EffectDag_get_InnerShadowEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_InnerShadowEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_InnerShadowEffect,self.Ptr)
        ret = None if intPtr==None else InnerShadowEffect(intPtr)
        return ret


    @InnerShadowEffect.setter
    def InnerShadowEffect(self, value:'InnerShadowEffect'):
        GetDllLibPpt().EffectDag_set_InnerShadowEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_InnerShadowEffect,self.Ptr, value.Ptr)

    @property

    def OuterShadowEffect(self)->'OuterShadowEffect':
        """
        Gets or sets the outer shadow effect.
        
        Returns:
            OuterShadowEffect: The outer shadow effect object.
        """
        GetDllLibPpt().EffectDag_get_OuterShadowEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_OuterShadowEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_OuterShadowEffect,self.Ptr)
        ret = None if intPtr==None else OuterShadowEffect(intPtr)
        return ret


    @OuterShadowEffect.setter
    def OuterShadowEffect(self, value:'OuterShadowEffect'):
        GetDllLibPpt().EffectDag_set_OuterShadowEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_OuterShadowEffect,self.Ptr, value.Ptr)

    @property

    def PresetShadowEffect(self)->'PresetShadow':
        """
        Gets or sets the preset shadow effect.
        
        Returns:
            PresetShadow: The preset shadow effect object.
        """
        GetDllLibPpt().EffectDag_get_PresetShadowEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_PresetShadowEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_PresetShadowEffect,self.Ptr)
        ret = None if intPtr==None else PresetShadow(intPtr)
        return ret


    @PresetShadowEffect.setter
    def PresetShadowEffect(self, value:'PresetShadow'):
        GetDllLibPpt().EffectDag_set_PresetShadowEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_PresetShadowEffect,self.Ptr, value.Ptr)

    @property

    def ReflectionEffect(self)->'ReflectionEffect':
        """
        Gets or sets the reflection effect.
        
        Returns:
            ReflectionEffect: The reflection effect object.
        """
        GetDllLibPpt().EffectDag_get_ReflectionEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_ReflectionEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_ReflectionEffect,self.Ptr)
        ret = None if intPtr==None else ReflectionEffect(intPtr)
        return ret


    @ReflectionEffect.setter
    def ReflectionEffect(self, value:'ReflectionEffect'):
        GetDllLibPpt().EffectDag_set_ReflectionEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_ReflectionEffect,self.Ptr, value.Ptr)

    @property

    def SoftEdgeEffect(self)->'SoftEdgeEffect':
        """
        Gets or sets the soft edge effect.
        
        Returns:
            SoftEdgeEffect: The soft edge effect object.
        """
        GetDllLibPpt().EffectDag_get_SoftEdgeEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_SoftEdgeEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_SoftEdgeEffect,self.Ptr)
        ret = None if intPtr==None else SoftEdgeEffect(intPtr)
        return ret


    @SoftEdgeEffect.setter
    def SoftEdgeEffect(self, value:'SoftEdgeEffect'):
        GetDllLibPpt().EffectDag_set_SoftEdgeEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_SoftEdgeEffect,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if the current EffectDag is equal to another object.

        Args:
            obj: The object to compare with the current object

        Returns:
            bool: True if the specified object is equal to the current object; otherwise, False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().EffectDag_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EffectDag_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectDag_Equals,self.Ptr, intPtrobj)
        return ret

