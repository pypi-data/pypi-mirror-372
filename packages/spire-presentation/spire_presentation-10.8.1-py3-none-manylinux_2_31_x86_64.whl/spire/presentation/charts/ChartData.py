from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartData (SpireObject) :
    """
    Represents the data associated with a chart.
    
    This class provides access to individual cells or ranges of cells within the chart's data source.
    It includes methods to retrieve specific data points and clear data ranges.
    """

    @dispatch
    def __getitem__(self, row,column):
        """
        Accesses a single cell in the chart data by row and column indices.
        
        Args:
            row: Row index (0-based)
            column: Column index (0-based)
            
        Returns:
            CellRange: Object representing the requested cell
        """
        
        GetDllLibPpt().ChartData_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ChartData_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_Item,self.Ptr, row,column)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret

    @dispatch
    def __getitem__(self, startRow,startColumn,endRow,endColumn):
        """
        Accesses a range of cells in the chart data.
        
        Args:
            startRow: Starting row index
            startColumn: Starting column index
            endRow: Ending row index
            endColumn: Ending column index
            
        Returns:
            CellRanges: Collection of cells in the specified range
        """
        
        GetDllLibPpt().ChartData_get_ItemRCLL.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibPpt().ChartData_get_ItemRCLL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemRCLL,self.Ptr, startRow,startColumn,endRow,endColumn)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret

    @dispatch
    def __getitem__(self, name:str):
        """
        Accesses a cell by its Excel-style name (e.g., "A1").
        
        Args:
            name: Cell reference in Excel format
            
        Returns:
            CellRange: Object representing the requested cell
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().ChartData_get_ItemN.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ChartData_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemN,self.Ptr,namePtr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret

    @dispatch

    def get_Item(self ,row:int,column:int)->CellRange:
        """
        Retrieves a specific cell in the chart data.
        
        Args:
            row: Row index (0-based)
            column: Column index (0-based)
            
        Returns:
            CellRange: Object representing the requested cell
        """
        
        GetDllLibPpt().ChartData_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ChartData_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_Item,self.Ptr, row,column)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def Clear(self ,row:int,column:int,lastRow:int,lastColumn:int):
        """
        Clears data within the specified range.
        
        Args:
            row: Starting row index
            column: Starting column index
            lastRow: Ending row index
            lastColumn: Ending column index
        """
        GetDllLibPpt().ChartData_Clear.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibPpt().ChartData_Clear,self.Ptr, row,column,lastRow,lastColumn)

    @dispatch

    def get_Item(self ,row:int,column:int,lastRow:int,lastColumn:int)->CellRanges:
        """
        Retrieves a range of cells.
        
        Args:
            row: Starting row index
            column: Starting column index
            lastRow: Ending row index
            lastColumn: Ending column index
            
        Returns:
            CellRanges: Collection of cells in the specified range
        """
        GetDllLibPpt().ChartData_get_ItemRCLL.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibPpt().ChartData_get_ItemRCLL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemRCLL,self.Ptr, row,column,lastRow,lastColumn)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @dispatch

    def get_Item(self ,worksheetIndex:int,row:int,column:int,lastRow:int,lastColumn:int)->CellRanges:
        """
        Retrieves a range of cells from a specific worksheet.
        
        Args:
            worksheetIndex: Index of the worksheet
            row: Starting row index
            column: Starting column index
            lastRow: Ending row index
            lastColumn: Ending column index
            
        Returns:
            CellRanges: Collection of cells in the specified range
        """
        
        GetDllLibPpt().ChartData_get_ItemWRCLL.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int]
        GetDllLibPpt().ChartData_get_ItemWRCLL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemWRCLL,self.Ptr, worksheetIndex,row,column,lastRow,lastColumn)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->CellRange:
        """
        Retrieves a cell by its Excel-style name.
        
        Args:
            name: Cell reference in Excel format
            
        Returns:
            CellRange: Object representing the requested cell
        """
        namePtr = StrToPtr(name)
        GetDllLibPpt().ChartData_get_ItemN.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ChartData_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemN,self.Ptr,namePtr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str,endCellName:str)->CellRanges:
        """
        Retrieves a range of cells by starting and ending Excel-style names.
        
        Args:
            name: Starting cell reference
            endCellName: Ending cell reference
            
        Returns:
            CellRanges: Collection of cells in the specified range
        """
        namePtr = StrToPtr(name)
        endCellNamePtr = StrToPtr(endCellName)
        GetDllLibPpt().ChartData_get_ItemNE.argtypes=[c_void_p ,c_char_p,c_char_p]
        GetDllLibPpt().ChartData_get_ItemNE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemNE,self.Ptr,namePtr,endCellNamePtr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @dispatch

    def get_Item(self ,worksheetIndex:int,name:str)->CellRange:
        """
        Retrieves a cell from a specific worksheet by Excel-style name.
        
        Args:
            worksheetIndex: Index of the worksheet
            name: Cell reference in Excel format
            
        Returns:
            CellRange: Object representing the requested cell
        """
        namePtr = StrToPtr(name)
        GetDllLibPpt().ChartData_get_ItemWN.argtypes=[c_void_p ,c_int,c_char_p]
        GetDllLibPpt().ChartData_get_ItemWN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemWN,self.Ptr, worksheetIndex,namePtr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,worksheetIndex:int,name:str,endCellName:str)->CellRanges:
        """
        Retrieves a range of cells from a specific worksheet.
        
        Args:
            worksheetIndex: Index of the worksheet
            name: Starting cell reference
            endCellName: Ending cell reference
            
        Returns:
            CellRanges: Collection of cells in the specified range
        """
        namePtr = StrToPtr(name)
        endCellNamePtr = StrToPtr(endCellName)
        GetDllLibPpt().ChartData_get_ItemWNE.argtypes=[c_void_p ,c_int,c_char_p,c_char_p]
        GetDllLibPpt().ChartData_get_ItemWNE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemWNE,self.Ptr, worksheetIndex,namePtr,endCellNamePtr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret
    

    @property
    def LastRowIndex(self)->int:
        """
        Gets the index of the last row containing data.
        
        Returns:
            int: 0-based index of the last data row
        """
        GetDllLibPpt().ChartData_LastRowIndex.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartData_LastRowIndex,self.Ptr)
        return ret
    
    @property
    def LastColIndex(self)->int:
        """
        Gets the index of the last column containing data.
        
        Returns:
            int: 0-based index of the last data column
        """
        GetDllLibPpt().ChartData_LastColIndex.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartData_LastColIndex,self.Ptr)
        return ret


