from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CellRange (SpireObject) :
    """
    Represents a cell range used as a data source for charts.
    Stores location and value information for chart data points.
    """
    @property
    def Row(self)->int:
        """
        Gets the row index of the cell.
        
        Returns:
            int: Zero-based row index.
        """
        GetDllLibPpt().CellRange_get_Row.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_Row.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRange_get_Row,self.Ptr)
        return ret

    @property
    def Column(self)->int:
        """
        Gets the column index of the cell.
        
        Returns:
            int: Zero-based column index.
        """
        GetDllLibPpt().CellRange_get_Column.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_Column.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRange_get_Column,self.Ptr)
        return ret

    @property
    def NumberValue(self)->float:
        """
        Gets or sets the numeric value of the cell.
        
        Returns:
            float: The numeric value of the cell
        """
        GetDllLibPpt().CellRange_get_NumberValue.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_NumberValue.restype=c_double
        ret = CallCFunction(GetDllLibPpt().CellRange_get_NumberValue,self.Ptr)
        return ret

    @NumberValue.setter
    def NumberValue(self, value:float):
        GetDllLibPpt().CellRange_set_NumberValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().CellRange_set_NumberValue,self.Ptr, value)

    @property

    def Text(self)->str:
        """
        Gets or sets the string value of the cell.
        
        Returns:
            str: The textual content of the cell
        """
        GetDllLibPpt().CellRange_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().CellRange_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().CellRange_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().CellRange_set_Text,self.Ptr,valuePtr)

    @property

    def Value(self)->'SpireObject':
        """
        Gets or sets the underlying value object of the cell.
        
        Returns:
            SpireObject: The raw value object of the cell
        """
        GetDllLibPpt().CellRange_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_Value.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellRange_get_Value,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Value.setter
    def Value(self, value:'SpireObject'):
        GetDllLibPpt().CellRange_set_Value.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().CellRange_set_Value,self.Ptr, value.Ptr)

    @property

    def WorksheetName(self)->str:
        """
        Gets the name of the worksheet containing this cell.
        
        Returns:
            str: The name of the parent worksheet
        """
        GetDllLibPpt().CellRange_get_WorksheetName.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_WorksheetName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().CellRange_get_WorksheetName,self.Ptr))
        return ret


    @property
    def WorksheetIndex(self)->int:
        """
        Gets the zero-based index of the worksheet containing this cell.
        
        Returns:
            int: The index of the parent worksheet
        """
        GetDllLibPpt().CellRange_get_WorksheetIndex.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_WorksheetIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRange_get_WorksheetIndex,self.Ptr)
        return ret

    @dispatch

    def Equals(self ,cellRange:'CellRange')->bool:
        """
        Determines if this cell range is equal to another specified cell range.
        
        Compares both position and content of the cells.
        
        Args:
            cellRange (CellRange): The cell range to compare with
            
        Returns:
            bool: True if the cell ranges are identical, otherwise False
        """
        intPtrcellRange:c_void_p = cellRange.Ptr

        GetDllLibPpt().CellRange_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CellRange_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CellRange_Equals,self.Ptr, intPtrcellRange)
        return ret

    @dispatch

    def Equals(self ,obj:SpireObject)->bool:
        """
        Determines if this cell range is equal to another specified object.
        
        Args:
            obj (SpireObject): The object to compare with
            
        Returns:
            bool: True if the objects are identical cell ranges, otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().CellRange_EqualsO.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CellRange_EqualsO.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CellRange_EqualsO,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
        Generates a hash code for this cell range.
        
        Returns:
            int: A hash code value for the current object
        """
        GetDllLibPpt().CellRange_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRange_GetHashCode,self.Ptr)
        return ret

    @property

    def NumberFormat(self)->str:
        """
        Gets or sets the number formatting string for numeric values.
        
        Returns:
            str: The current number format string
        """
        GetDllLibPpt().CellRange_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().CellRange_get_NumberFormat,self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().CellRange_set_NumberFormat.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().CellRange_set_NumberFormat,self.Ptr,valuePtr)

