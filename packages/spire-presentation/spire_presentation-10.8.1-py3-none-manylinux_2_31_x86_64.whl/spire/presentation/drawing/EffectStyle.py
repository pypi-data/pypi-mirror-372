from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectStyle (SpireObject) :
    """
    Represents an effect style that can be applied to presentation elements.
    
    Attributes:
        EffectDag (EffectDag): Gets the effect format settings (read-only).
        FormatThreeDFormat (FormatThreeD): Gets the 3D format settings (read-only).
    """
    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets the effect format settings for this style.
        """
        GetDllLibPpt().EffectStyle_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyle_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyle_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def FormatThreeDFormat(self)->'FormatThreeD':
        """
        Gets the 3D format settings for this style.
        """
        GetDllLibPpt().EffectStyle_get_FormatThreeDFormat.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyle_get_FormatThreeDFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyle_get_FormatThreeDFormat,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current EffectStyle is equal to another object.
        
        Args:
            obj: The object to compare with the current EffectStyle.
            
        Returns:
            bool: True if the specified object is equal to the current EffectStyle; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().EffectStyle_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EffectStyle_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectStyle_Equals,self.Ptr, intPtrobj)
        return ret

