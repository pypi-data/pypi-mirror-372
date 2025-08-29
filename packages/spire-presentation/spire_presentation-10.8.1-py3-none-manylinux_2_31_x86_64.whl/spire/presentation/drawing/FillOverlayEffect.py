from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillOverlayEffect (  ImageTransformBase) :
    """
    Represents a fill overlay effect that combines an additional fill with the original fill using blending.
    
    Used to create complex fill effects by merging two different fill formats.
    """
    @property

    def FillFormat(self)->'FillFormat':
        """
        Gets or sets the fill format used for the overlay effect.
        
        Returns:
            FillFormat: Fill properties for the overlay
        """
        GetDllLibPpt().FillOverlayEffect_get_FillFormat.argtypes=[c_void_p]
        GetDllLibPpt().FillOverlayEffect_get_FillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillOverlayEffect_get_FillFormat,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @FillFormat.setter
    def FillFormat(self, value:'FillFormat'):
        """
        Sets the fill format used for the overlay effect.
        
        Args:
            value: New fill format to apply
        """
        GetDllLibPpt().FillOverlayEffect_set_FillFormat.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().FillOverlayEffect_set_FillFormat,self.Ptr, value.Ptr)

    @property

    def Blend(self)->'BlendMode':
        """
        Gets or sets the blending mode used to combine the overlay fill with the base fill.
        
        Returns:
            BlendMode: Current blending mode
        """
        GetDllLibPpt().FillOverlayEffect_get_Blend.argtypes=[c_void_p]
        GetDllLibPpt().FillOverlayEffect_get_Blend.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillOverlayEffect_get_Blend,self.Ptr)
        objwraped = BlendMode(ret)
        return objwraped

    @Blend.setter
    def Blend(self, value:'BlendMode'):
        """
        Sets the blending mode used to combine the overlay fill with the base fill.
        
        Args:
            value: New blending mode to apply
        """
        GetDllLibPpt().FillOverlayEffect_set_Blend.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().FillOverlayEffect_set_Blend,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current fill overlay effect is equal to another object.
        
        Args:
            obj: The object to compare with
        
        Returns:
            bool: True if the objects are equal, otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillOverlayEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillOverlayEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillOverlayEffect_Equals,self.Ptr, intPtrobj)
        return ret

