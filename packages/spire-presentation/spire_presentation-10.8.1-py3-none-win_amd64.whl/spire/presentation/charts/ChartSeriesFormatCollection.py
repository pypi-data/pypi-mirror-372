from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartSeriesFormatCollection (SpireObject) :
    """
    Represents a collection of ChartSeriesDataFormat objects.
    """
    @property

    def SeriesLabel(self)->'CellRanges':
        """
        Gets or sets the chart series value.
        """
        GetDllLibPpt().ChartSeriesFormatCollection_get_SeriesLabel.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_get_SeriesLabel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_SeriesLabel,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @SeriesLabel.setter
    def SeriesLabel(self, value:'CellRanges'):
        GetDllLibPpt().ChartSeriesFormatCollection_set_SeriesLabel.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_set_SeriesLabel,self.Ptr, value.Ptr)


    @dispatch
    def __getitem__(self, index):
        """
        Gets the element at the specified index.
        
        Args:
            index: The zero-based index of the element to get.
        
        Returns:
            The element at the specified index.
        
        Raises:
            StopIteration: If index is equal to or greater than Count.
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().ChartSeriesFormatCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartSeriesFormatCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartSeriesDataFormat(intPtr)
        return ret

    def get_Item(self ,index:int)->'ChartSeriesDataFormat':
        """
        Gets the element at the specified index.
        
        Args:
            index: The zero-based index of the element to get.
        
        Returns:
            The element at the specified index.
        """
        
        GetDllLibPpt().ChartSeriesFormatCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartSeriesFormatCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartSeriesDataFormat(intPtr)
        return ret

    @property
    def Count(self)->int:
        """
        Gets the number of elements actually contained in the collection.
        Read-only int.
        """
        GetDllLibPpt().ChartSeriesFormatCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_Count,self.Ptr)
        return ret

    
    def AppendCellRange(self ,cellRange:'CellRange')->int:
        """
        Appends a cell range to the collection.
        
        Args:
            cellRange: The cell range to append.
        
        Returns:
            The index at which the value has been added.
        """
        
        intPtrcellRange:c_void_p = cellRange.Ptr
        
        GetDllLibPpt().ChartSeriesFormatCollection_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_Append,self.Ptr, intPtrcellRange)
        return ret


    def AppendStr(self ,value:str)->int:
        """
        Appends a string value to the collection.
        
        Args:
            value: The string value to append.
        
        Returns:
            The index at which the value has been added.
        """
        
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_AppendV,self.Ptr,valuePtr)
        return ret


    def AppendFloat(self ,value:float)->int:
        """
        Appends a numeric value to the collection.
        
        Args:
            value: The float value to append.
        
        Returns:
            The index at which the value has been added.
        """
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV1.argtypes=[c_void_p ,c_float]
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV1.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_AppendV1,self.Ptr, value)
        return ret


    def AppendSpireObject(self ,value:SpireObject)->int:
        """
        Appends a SpireObject value to the collection.
        
        Args:
            value: The SpireObject to append.
        
        Returns:
            The index at which the value has been added.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartSeriesFormatCollection_AppendV11.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV11.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_AppendV11,self.Ptr, intPtrvalue)
        return ret


    def IndexOf(self ,value:'ChartSeriesDataFormat')->int:
        """
        Searches for the specified ChartSeriesDataFormat and returns its index.
        
        Args:
            value: The ChartSeriesDataFormat to locate.
        
        Returns:
            The zero-based index of the first occurrence, or -1 if not found.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartSeriesFormatCollection_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_IndexOf,self.Ptr, intPtrvalue)
        return ret


    def Remove(self ,value:'ChartSeriesDataFormat'):
        """
        Removes the specified ChartSeriesDataFormat from the collection.
        
        Args:
            value: The ChartSeriesDataFormat to remove.
        
        Raises:
            ArgumentException: If the value is not found in the collection.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartSeriesFormatCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_Remove,self.Ptr, intPtrvalue)

    def RemoveAt(self ,value:'int'):
        """
        Removes the element at the specified index.
        
        Args:
            value: The zero-based index of the element to remove.
        """
        intPtrvalue:c_void_p = value

        GetDllLibPpt().ChartSeriesFormatCollection_RemoveAt.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_RemoveAt,self.Ptr, intPtrvalue)

    def Clear(self):
        """
        Removes all elements from the collection.
        """

        GetDllLibPpt().ChartSeriesFormatCollection_clear.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_clear,self.Ptr)

    @property
    def KeepSeriesFormat(self)->bool:
        """
        Gets or sets whether to keep series format when resetting SeriesLabel.
        """
        GetDllLibPpt().ChartSeriesFormatCollection_get_KeepSeriesFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_get_KeepSeriesFormat.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_KeepSeriesFormat,self.Ptr)
        return ret

    @KeepSeriesFormat.setter
    def KeepSeriesFormat(self, value:bool):
        GetDllLibPpt().ChartSeriesFormatCollection_set_KeepSeriesFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_set_KeepSeriesFormat,self.Ptr, value)

    @property
    def Capacity(self)->int:
        """
        Gets or sets the total number of elements the collection can hold.
        """
        GetDllLibPpt().ChartSeriesFormatCollection_getCapacity.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_getCapacity,self.Ptr)
        return ret
    
    @Capacity.setter
    def Capacity(self, value:int)->int:
        """
        """

        GetDllLibPpt().ChartSeriesFormatCollection_setCapacity.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_setCapacity,self.Ptr,value)

