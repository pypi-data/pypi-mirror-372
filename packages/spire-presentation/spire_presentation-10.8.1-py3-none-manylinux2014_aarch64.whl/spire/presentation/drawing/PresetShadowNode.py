from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PresetShadowNode (  EffectNode) :
    """
    Represents a preset shadow effect node in a presentation effect chain.
    
    This class provides read-only access to preset shadow effect properties 
    when applied as part of a node-based effect configuration.
    """
    @property
    def Direction(self)->float:
        """
        Gets the direction angle of the shadow effect.
        
        Returns:
            float: The direction angle of the shadow in degrees
        """
        GetDllLibPpt().PresetShadowNode_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().PresetShadowNode_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().PresetShadowNode_get_Direction,self.Ptr)
        return ret

    @property
    def Distance(self)->float:
        """
        Gets the distance of the shadow from the object.
        
        Returns:
            float: The shadow distance value
        """
        GetDllLibPpt().PresetShadowNode_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().PresetShadowNode_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().PresetShadowNode_get_Distance,self.Ptr)
        return ret

    @property

    def ShadowColor(self)->'Color':
        """
        Gets the color of the shadow effect.
        
        Returns:
            Color: The color configuration of the shadow
        """
        GetDllLibPpt().PresetShadowNode_get_ShadowColor.argtypes=[c_void_p]
        GetDllLibPpt().PresetShadowNode_get_ShadowColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PresetShadowNode_get_ShadowColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def Preset(self)->'PresetShadowValue':
        """
        Gets the predefined shadow effect type.
        
        Returns:
            PresetShadowValue: The preset shadow type
        """
        GetDllLibPpt().PresetShadowNode_get_Preset.argtypes=[c_void_p]
        GetDllLibPpt().PresetShadowNode_get_Preset.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PresetShadowNode_get_Preset,self.Ptr)
        objwraped = PresetShadowValue(ret)
        return objwraped

