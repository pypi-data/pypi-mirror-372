from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeAdjust (SpireObject) :
    """
    Represents an adjustment value for a shape in a presentation.
    This class encapsulates both the numeric value and metadata of a shape adjustment.
    """
    @property
    def Value(self)->float:
        """
        Gets or sets the adjustment value.
        Represents the numeric value of the shape adjustment.

        Returns:
            float: The current adjustment value
        """
        GetDllLibPpt().ShapeAdjust_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjust_get_Value.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ShapeAdjust_get_Value,self.Ptr)
        return ret

    @Value.setter
    def Value(self, value:float):
        GetDllLibPpt().ShapeAdjust_set_Value.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ShapeAdjust_set_Value,self.Ptr, value)

    @property

    def Name(self)->str:
        """
        Gets the name of this adjustment value.
        Provides identifier information for the adjustment.

        Returns:
            str: The name of the adjustment
        """
        GetDllLibPpt().ShapeAdjust_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjust_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ShapeAdjust_get_Name,self.Ptr))
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this adjustment is equal to another object.

        Args:
            obj (SpireObject): The object to compare with
        Returns:
            bool: True if the objects are equal, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShapeAdjust_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeAdjust_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeAdjust_Equals,self.Ptr, intPtrobj)
        return ret

