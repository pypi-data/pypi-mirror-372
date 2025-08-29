from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeAdjustmentList (SpireObject) :
    """
    Represents a collection of shape adjustments.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of adjustments in the collection.

        Returns:
            int: Total number of adjustments
        """
        GetDllLibPpt().ShapeAdjustmentList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjustmentList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeAdjustmentList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'ShapeAdjust':
        """
        Retrieves a shape adjustment by its index in the collection.

        Args:
            index (int): The zero-based index of the adjustment
        Returns:
            ShapeAdjust: The adjustment object at the specified index
        """
        
        GetDllLibPpt().ShapeAdjustmentList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ShapeAdjustmentList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeAdjustmentList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ShapeAdjust(intPtr)
        return ret


