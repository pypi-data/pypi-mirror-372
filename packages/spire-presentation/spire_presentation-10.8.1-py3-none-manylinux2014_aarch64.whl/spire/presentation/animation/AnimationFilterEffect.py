from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationFilterEffect (  CommonBehavior) :
    """
    Represents a filter effect for an animation behavior.
    
    This class controls how filter effects are applied during animations.
    """
    @property

    def Reveal(self)->'FilterRevealType':
        """
        Determines how embedded objects will be revealed during animation.
        
        Returns:
            FilterRevealType: The reveal type setting.
        """
        GetDllLibPpt().AnimationFilterEffect_get_Reveal.argtypes=[c_void_p]
        GetDllLibPpt().AnimationFilterEffect_get_Reveal.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationFilterEffect_get_Reveal,self.Ptr)
        objwraped = FilterRevealType(ret)
        return objwraped

    @Reveal.setter
    def Reveal(self, value:'FilterRevealType'):
        """
        Sets how embedded objects will be revealed during animation.
        
        Args:
            value: The reveal type to set.
        """
        GetDllLibPpt().AnimationFilterEffect_set_Reveal.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationFilterEffect_set_Reveal,self.Ptr, value.value)

    @property

    def Type(self)->'FilterEffectType':
        """
        Gets the type of animation effect.
        
        Returns:
            FilterEffectType: The type of animation.
        """
        GetDllLibPpt().AnimationFilterEffect_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().AnimationFilterEffect_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationFilterEffect_get_Type,self.Ptr)
        objwraped = FilterEffectType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'FilterEffectType'):
        """
        Sets the type of animation effect.
        
        Args:
            value: The animation type to set.
        """
        GetDllLibPpt().AnimationFilterEffect_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationFilterEffect_set_Type,self.Ptr, value.value)

    @property

    def Subtype(self)->'FilterEffectSubtype':
        """
        Gets the subtype of the filter effect.
        
        Returns:
            FilterEffectSubtype: The subtype of the effect.
        """
        GetDllLibPpt().AnimationFilterEffect_get_Subtype.argtypes=[c_void_p]
        GetDllLibPpt().AnimationFilterEffect_get_Subtype.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationFilterEffect_get_Subtype,self.Ptr)
        objwraped = FilterEffectSubtype(ret)
        return objwraped

    @Subtype.setter
    def Subtype(self, value:'FilterEffectSubtype'):
        """
        Sets the subtype of the filter effect.
        
        Args:
            value: The subtype to set.
        """
        GetDllLibPpt().AnimationFilterEffect_set_Subtype.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationFilterEffect_set_Subtype,self.Ptr, value.value)

