from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Backdrop (  PptObject) :
    """
    Represents a 3D backdrop effect configuration.
    
    Attributes:
        NormalVector (List[float]): Normal vector in 3D space.
        AnchorPoint (List[float]): Anchor point in 3D space.
        UpVector (List[float]): Up direction vector.
    
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Indicates whether two Backdrop instances are equal.

        Args:
            obj: The Backdrop to compare with the current Tabs

        Returns:
            bool: True if the specified Tabs is equal to the current Backdrop, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Backdrop_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Backdrop_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Backdrop_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def NormalVector(self)->List[float]:
        """Gets or sets the normal vector defining the backdrop orientation."""
        GetDllLibPpt().Backdrop_get_NormalVector.argtypes=[c_void_p]
        GetDllLibPpt().Backdrop_get_NormalVector.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Backdrop_get_NormalVector,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret

    @NormalVector.setter
    def NormalVector(self, value:List[float]):
        vCount = len(value)
        ArrayType = c_float * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibPpt().Backdrop_set_NormalVector.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibPpt().Backdrop_set_NormalVector,self.Ptr, vArray, vCount)

    @property

    def AnchorPoint(self)->List[float]:
        """Gets or sets the anchor point position in 3D space."""
        GetDllLibPpt().Backdrop_get_AnchorPoint.argtypes=[c_void_p]
        GetDllLibPpt().Backdrop_get_AnchorPoint.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Backdrop_get_AnchorPoint,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret

    @AnchorPoint.setter
    def AnchorPoint(self, value:List[float]):
        vCount = len(value)
        ArrayType = c_float * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibPpt().Backdrop_set_AnchorPoint.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibPpt().Backdrop_set_AnchorPoint,self.Ptr, vArray, vCount)

    @property

    def UpVector(self)->List[float]:
        """Gets or sets the up direction vector."""
        GetDllLibPpt().Backdrop_get_UpVector.argtypes=[c_void_p]
        GetDllLibPpt().Backdrop_get_UpVector.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Backdrop_get_UpVector,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret

    @UpVector.setter
    def UpVector(self, value:List[float]):
        vCount = len(value)
        ArrayType = c_float * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibPpt().Backdrop_set_UpVector.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibPpt().Backdrop_set_UpVector,self.Ptr, vArray, vCount)

