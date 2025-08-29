from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SoftEdgeNode (  EffectNode) :
    """
    Represents a soft edge effect node where shape edges are blurred while the fill remains unaffected.
    """
    @property
    def Radius(self)->float:
        """
        Gets the blur radius applied to shape edges.

        Returns:
            float: The current blur radius value
        """
        GetDllLibPpt().SoftEdgeNode_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().SoftEdgeNode_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().SoftEdgeNode_get_Radius,self.Ptr)
        return ret

