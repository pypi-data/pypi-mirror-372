from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SoftEdgeEffect (SpireObject) :
    """
    Represents a soft edge effect where the edges of a shape are blurred while the fill remains unaffected.
    """
    @property
    def Radius(self)->float:
        """
        Gets or sets the radius of blur applied to the edges.

        Returns:
            float: The current blur radius value
        """
        GetDllLibPpt().SoftEdgeEffect_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().SoftEdgeEffect_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().SoftEdgeEffect_get_Radius,self.Ptr)
        return ret

    @Radius.setter
    def Radius(self, value:float):
        GetDllLibPpt().SoftEdgeEffect_set_Radius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().SoftEdgeEffect_set_Radius,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current SoftEdgeEffect is equal to another object.

        Args:
            obj (SpireObject): The object to compare with the current effect

        Returns:
            bool: True if the objects are equivalent, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SoftEdgeEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SoftEdgeEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SoftEdgeEffect_Equals,self.Ptr, intPtrobj)
        return ret

