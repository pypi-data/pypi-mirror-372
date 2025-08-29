from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ChartDataPointCollection (  IEnumerable) :
    """
    Represents a collection of ChartPoint.
    """

    def get_Item(self ,index:int)->'ChartDataPoint':
        """
        Gets the element at the specified index.

        Args:
            index (int): The zero-based index of the element to get

        Returns:
            ChartDataPoint: The ChartDataPoint at the specified index
        """
        GetDllLibPpt().ChartDataPointCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartDataPointCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPointCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartDataPoint(intPtr)
        return ret



    def Add(self ,value:'ChartDataPoint')->int:
        """
        Adds a new DataLabel at the end of the collection.

        Args:
            value (ChartDataPoint): The ChartDataPoint to add

        Returns:
            int: The index at which the value has been added
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartDataPointCollection_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartDataPointCollection_Add.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPointCollection_Add,self.Ptr, intPtrvalue)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the entire collection.

        Returns:
            IEnumerator: An IEnumerator for the entire collection
        """
        GetDllLibPpt().ChartDataPointCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPointCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPointCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
        Gets the number of elements contained in the collection.

        Returns:
            int: The number of elements actually contained in the collection
        """
        GetDllLibPpt().ChartDataPointCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPointCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPointCollection_get_Count,self.Ptr)
        return ret

