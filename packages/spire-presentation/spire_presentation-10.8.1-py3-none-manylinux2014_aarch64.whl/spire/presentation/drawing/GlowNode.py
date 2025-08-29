from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GlowNode (  EffectNode) :
    """
    Represents a glow effect applied to presentation elements, adding a 
    blurred color outline outside object edges.
    """
    @property
    def Radius(self)->float:
        """
        Gets the blur radius of the glow effect (read-only).
        """
        GetDllLibPpt().GlowNode_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().GlowNode_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().GlowNode_get_Radius,self.Ptr)
        return ret

    @property

    def Color(self)->'Color':
        """
        Gets the color of the glow effect (read-only).
        """
        GetDllLibPpt().GlowNode_get_Color.argtypes=[c_void_p]
        GetDllLibPpt().GlowNode_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GlowNode_get_Color,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


