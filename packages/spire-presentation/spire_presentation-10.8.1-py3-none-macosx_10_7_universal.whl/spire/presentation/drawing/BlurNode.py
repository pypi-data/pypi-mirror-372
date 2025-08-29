from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlurNode (  EffectNode) :
    """
    Represents a blur effect applied to an entire shape including its fill.
    Affects all color channels including alpha. Read-only properties.
    """
    @property
    def Radius(self)->float:
        """Gets the blur radius (read-only)."""
        GetDllLibPpt().BlurNode_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().BlurNode_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().BlurNode_get_Radius,self.Ptr)
        return ret

    @property
    def Grow(self)->bool:
        """Checks if effect spreads beyond shape borders (read-only)."""
        GetDllLibPpt().BlurNode_get_Grow.argtypes=[c_void_p]
        GetDllLibPpt().BlurNode_get_Grow.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().BlurNode_get_Grow,self.Ptr)
        return ret

