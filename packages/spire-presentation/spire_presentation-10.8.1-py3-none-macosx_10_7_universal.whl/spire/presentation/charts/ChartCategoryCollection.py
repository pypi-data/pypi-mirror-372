from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartCategoryCollection (SpireObject) :
    """
    Represents a collection of ChartCategory objects in a chart.
    Provides methods to manage categories including adding, removing, and accessing items.
    """

    def get_Item(self ,index:int)->'ChartCategory':
        """
        Gets the ChartCategory at the specified index.
        
        Args:
            index (int): The zero-based index of the category to retrieve.
        
        Returns:
            ChartCategory: The category at the specified index.
        """
        
        GetDllLibPpt().ChartCategoryCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartCategoryCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartCategoryCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartCategory(intPtr)
        return ret


    @property

    def CategoryLabels(self)->'CellRanges':
        """
        Gets or sets the cell ranges containing category labels.
        
        Returns:
            CellRanges: The collection of cell ranges defining category labels.
        """
        GetDllLibPpt().ChartCategoryCollection_get_CategoryLabels.argtypes=[c_void_p]
        GetDllLibPpt().ChartCategoryCollection_get_CategoryLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartCategoryCollection_get_CategoryLabels,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @CategoryLabels.setter
    def CategoryLabels(self, value:'CellRanges'):
        GetDllLibPpt().ChartCategoryCollection_set_CategoryLabels.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategoryCollection_set_CategoryLabels,self.Ptr, value.Ptr)


    def AppendCellRange(self ,cellRange:'CellRange')->int:
        """
        Creates a new chart category from a CellRange and adds it to the collection.
        
        Args:
            cellRange (CellRange): The cell range to create the category from.
        
        Returns:
            int: Index of the newly added category.
        """
        intPtrcellRange:c_void_p = cellRange.Ptr

        GetDllLibPpt().ChartCategoryCollection_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartCategoryCollection_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_Append,self.Ptr, intPtrcellRange)
        return ret


    def AppendStr(self ,value:str)->int:
        """
        Appends a new category using a string value.
        
        Args:
            value (str): The string value for the new category.
        
        Returns:
            int: Index of the newly added category.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartCategoryCollection_AppendV.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ChartCategoryCollection_AppendV.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_AppendV,self.Ptr,valuePtr)
        return ret


    def AppendFloat(self ,value:float)->int:
        """
        Appends a new category using a numeric value.
        
        Args:
            value (float): The numeric value for the new category.
        
        Returns:
            int: Index of the newly added category.
        """
        GetDllLibPpt().ChartCategoryCollection_AppendV1.argtypes=[c_void_p ,c_float]
        GetDllLibPpt().ChartCategoryCollection_AppendV1.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_AppendV1,self.Ptr, value)
        return ret

    def AppendSpireObject(self ,value:SpireObject)->int:
        """
        Creates a new ChartCategory from a SpireObject and adds it to the collection.
        
        Args:
            value (SpireObject): The object to create the category from.
        
        Returns:
            int: Index of the newly added category.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartCategoryCollection_AppendV11.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartCategoryCollection_AppendV11.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_AppendV11,self.Ptr, intPtrvalue)
        return ret


    def IndexOf(self ,value:'ChartCategory')->int:
        """
        Searches for the specified ChartCategory and returns its index.
        
        Args:
            value (ChartCategory): The category to locate.
        
        Returns:
            int: Zero-based index if found; otherwise -1.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartCategoryCollection_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartCategoryCollection_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_IndexOf,self.Ptr, intPtrvalue)
        return ret


    def Remove(self ,value:'ChartCategory'):
        """
        Removes a specific category from the collection.
        
        Args:
            value (ChartCategory): The category to remove.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartCategoryCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategoryCollection_Remove,self.Ptr, intPtrvalue)

    @property
    def Count(self)->int:
        """
        Gets the number of categories in the collection.
        
        Returns:
            int: Total count of categories.
        """

        GetDllLibPpt().ChartCategoryCollection_GetCount.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_GetCount,self.Ptr)
        return ret

    def Clear(self):
        """
        Removes all categories from the collection.
        """
        GetDllLibPpt().ChartCategoryCollection_Clear.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategoryCollection_Clear,self.Ptr)

    @property
    def Capacity(self)->int:
        """
        Gets or sets the capacity of the collection.
        
        Returns:
            int: Current capacity of the collection.
        """
        GetDllLibPpt().ChartCategoryCollection_getCapacity.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_getCapacity,self.Ptr)
        return ret
    
    @Capacity.setter
    def Capacity(self, value:int)->int:
        """
        Sets the capacity of the collection.
        
        Args:
            value (int): The new capacity value.
        """
        GetDllLibPpt().ChartCategoryCollection_setCapacity.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategoryCollection_setCapacity,self.Ptr,value)

