from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ITable (IShape) :
    """
    Represents a table shape on a slide.
    Provides comprehensive control over table structure, formatting, and contents.
    """

    @dispatch
    def __getitem__(self, index):
        """
        Dual-index accessor for table elements:
        - Single index: Returns a row collection
        - Double index: Returns a specific cell

        Args:
            index: Single int or tuple of (column, row)

        Returns:
            TableRowCollection or Cell: Requested table component.
        """
        if(len(index) ==1):
            return self.TableRows[index[0]]
        if(len(index) ==2):
            column,row = index
            GetDllLibPpt().ITable_get_Item.argtypes=[c_void_p ,c_int,c_int]
            GetDllLibPpt().ITable_get_Item.restype=c_void_p
            intPtr = CallCFunction(GetDllLibPpt().ITable_get_Item,self.Ptr, column,row)
            ret = None if intPtr==None else Cell(intPtr)
            return ret


    @dispatch
    def get_Item(self ,column:int,row:int)->'Cell':
  
        """
        Retrieves a cell by column and row indexes.

        Args:
            column (int): Column index (0-based)
            row (int): Row index (0-based)

        Returns:
            Cell: The cell at the specified position.
        """
        GetDllLibPpt().ITable_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ITable_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Item,self.Ptr, column,row)
        ret = None if intPtr==None else Cell(intPtr)

    def MergeCells(self ,cell1:'Cell',cell2:'Cell',allowSplitting:bool):
        """
        Merges adjacent table cells.

        Args:
            cell1 (Cell): First cell to merge.
            cell2 (Cell): Second cell to merge.
            allowSplitting (bool): Whether to permit cell splitting during merge.
        """
        intPtrcell1:c_void_p = cell1.Ptr
        intPtrcell2:c_void_p = cell2.Ptr

        GetDllLibPpt().ITable_MergeCells.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
        CallCFunction(GetDllLibPpt().ITable_MergeCells,self.Ptr, intPtrcell1,intPtrcell2,allowSplitting)


    def SetTableBorder(self ,borderType:'TableBorderType',borderWidth:float,borderColor:'Color'):
        """
        Configures border styles for the entire table.

        Args:
            borderType (TableBorderType): Border style to apply.
            borderWidth (float): Thickness of the border lines.
            borderColor (Color): Color of the border lines.
        """
        enumborderType:c_int = borderType.value
        intPtrborderColor:c_void_p = borderColor.Ptr

        GetDllLibPpt().ITable_SetTableBorder.argtypes=[c_void_p ,c_int,c_double,c_void_p]
        CallCFunction(GetDllLibPpt().ITable_SetTableBorder,self.Ptr, enumborderType,borderWidth,intPtrborderColor)

    @property

    def StylePreset(self)->'TableStylePreset':
        """
        Gets or sets the predefined table style.

        Returns:
            TableStylePreset: Current built-in table style.
        """
        GetDllLibPpt().ITable_get_StylePreset.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_StylePreset.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITable_get_StylePreset,self.Ptr)
        objwraped = TableStylePreset(ret)
        return objwraped

    @StylePreset.setter
    def StylePreset(self, value:'TableStylePreset'):
        GetDllLibPpt().ITable_set_StylePreset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITable_set_StylePreset,self.Ptr, value.value)

    @property

    def TableRows(self)->'TableRowCollection':
        """
        Gets the collection of rows in the table.

        Returns:
            TableRowCollection: All rows in the table.
        """
        GetDllLibPpt().ITable_get_TableRows.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_TableRows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_TableRows,self.Ptr)
        ret = None if intPtr==None else TableRowCollection(intPtr)
        return ret


    @property

    def ColumnsList(self)->'ColumnCollection':
        """
        Gets the collection of columns in the table.

        Returns:
            ColumnCollection: All columns in the table.
        """
        GetDllLibPpt().ITable_get_ColumnsList.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_ColumnsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_ColumnsList,self.Ptr)
        ret = None if intPtr==None else ColumnCollection(intPtr)
        return ret


    @property
    def RightToLeft(self)->bool:
        """
        Indicates right-to-left reading order.

        Returns:
            bool: True for RTL layout, False for LTR.
        """
        GetDllLibPpt().ITable_get_RightToLeft.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_RightToLeft.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_RightToLeft,self.Ptr)
        return ret

    @RightToLeft.setter
    def RightToLeft(self, value:bool):
        GetDllLibPpt().ITable_set_RightToLeft.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_RightToLeft,self.Ptr, value)

    @property
    def FirstRow(self)->bool:
        """
        Sets right-to-left reading order.

        Args:
            value (bool): True for RTL layout, False for LTR.
        """
        GetDllLibPpt().ITable_get_FirstRow.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_FirstRow.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_FirstRow,self.Ptr)
        return ret

    @FirstRow.setter
    def FirstRow(self, value:bool):
        GetDllLibPpt().ITable_set_FirstRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_FirstRow,self.Ptr, value)

    @property
    def FirstCol(self)->bool:
        """
        Indicates whether the first column of a table has to be drawn with a special formatting.
        Read/write .
   
        """
        GetDllLibPpt().ITable_get_FirstCol.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_FirstCol.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_FirstCol,self.Ptr)
        return ret

    @FirstCol.setter
    def FirstCol(self, value:bool):
        GetDllLibPpt().ITable_set_FirstCol.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_FirstCol,self.Ptr, value)

    @property
    def LastRow(self)->bool:
        """
        Indicates whether the last row of a table has to be drawn with a special formatting.
        Read/write>.
    
        """
        GetDllLibPpt().ITable_get_LastRow.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_LastRow.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_LastRow,self.Ptr)
        return ret

    @LastRow.setter
    def LastRow(self, value:bool):
        GetDllLibPpt().ITable_set_LastRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_LastRow,self.Ptr, value)

    @property
    def LastCol(self)->bool:
        """
        Indicates whether the last column of a table has to be drawn with a special formatting.
        Read/write 
  
        """
        GetDllLibPpt().ITable_get_LastCol.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_LastCol.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_LastCol,self.Ptr)
        return ret

    @LastCol.setter
    def LastCol(self, value:bool):
        GetDllLibPpt().ITable_set_LastCol.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_LastCol,self.Ptr, value)

    @property
    def HorizontalBanding(self)->bool:
        """
        Indicates whether the even rows has to be drawn with a different formatting.
        Read/write 
        """
        GetDllLibPpt().ITable_get_HorizontalBanding.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_HorizontalBanding.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_HorizontalBanding,self.Ptr)
        return ret

    @HorizontalBanding.setter
    def HorizontalBanding(self, value:bool):
        GetDllLibPpt().ITable_set_HorizontalBanding.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_HorizontalBanding,self.Ptr, value)

    @property
    def VerticalBanding(self)->bool:
        """
        Indicates whether the even columns has to be drawn with a different formatting.
        Read/write <see cref="T:System.Boolean" />.
    
        """
        GetDllLibPpt().ITable_get_VerticalBanding.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_VerticalBanding.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_VerticalBanding,self.Ptr)
        return ret

    @VerticalBanding.setter
    def VerticalBanding(self, value:bool):
        GetDllLibPpt().ITable_set_VerticalBanding.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_VerticalBanding,self.Ptr, value)

    @property

    def ShapeLocking(self)->'GraphicalNodeLocking':
        """
        Gets lock type of shape.
        Read-only 
        """
        GetDllLibPpt().ITable_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else GraphicalNodeLocking(intPtr)
        return ret


    @property
    def IsPlaceholder(self)->bool:
        """
        Indicates whether the shape is Placeholder.
        Read-only 
        """
        GetDllLibPpt().ITable_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_IsPlaceholder,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
        Gets the placeholder for a shape.
        Read-only 
        """
        GetDllLibPpt().ITable_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the shape's tags collection.
        Read-only 
        """
        GetDllLibPpt().ITable_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets or sets the shape frame's properties.
        Read/write 
        """
        GetDllLibPpt().ITable_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().ITable_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ITable_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets the LineFormat object that contains line formatting properties for a shape.
        Read-only
        """
        GetDllLibPpt().ITable_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
        Gets the ThreeDFormat object that 3d effect properties for a shape.
            
        Note: can return null for certain types of shapes which don't have 3d properties.
   
        """
        GetDllLibPpt().ITable_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets the EffectFormat object which contains pixel effects applied to a shape.
            
        Note: can return null for certain types of shapes which don't have effect properties.
   
        """
        GetDllLibPpt().ITable_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets the FillFormat object that contains fill formatting properties for a shape.
        Read-only.
        Note: can return null for certain types of shapes which don't have fill properties.
    
        """
        GetDllLibPpt().ITable_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink defined for mouse click.
        Read/write 
        """
        GetDllLibPpt().ITable_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().ITable_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ITable_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink defined for mouse over.
        Read/write 
        """
        GetDllLibPpt().ITable_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().ITable_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ITable_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
        Indicates whether the shape is hidden.
        Read/write 
        """
        GetDllLibPpt().ITable_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().ITable_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
        Gets the parent slide of a shape.
        Read-only .
        """
        GetDllLibPpt().ITable_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
        Gets or sets the position of a shape in the z-order.
        Shapes[0] returns the shape at the back of the z-order,
        and Shapes[Shapes.Count - 1] returns the shape at the front of the z-order.
        Read/Write.
  
        """
        GetDllLibPpt().ITable_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITable_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().ITable_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITable_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
        Gets or sets the number of degrees the specified shape is rotated around
        the z-axis. A positive value indicates clockwise rotation; a negative value
        indicates counterclockwise rotation.
        Read/write .
   
        """
        GetDllLibPpt().ITable_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().ITable_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets or sets the x-coordinate of the upper-left corner of the shape.
        Read/write.
    
        """
        GetDllLibPpt().ITable_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().ITable_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets the y-coordinate of the upper-left corner of the shape.
        Read/write 
        """
        GetDllLibPpt().ITable_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().ITable_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets the width of the shape.
        Read/write .
    
        """
        GetDllLibPpt().ITable_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().ITable_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets the height of the shape.
        Read/write.
    
        """
        GetDllLibPpt().ITable_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().ITable_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
        Gets or sets the alternative text associated with a shape.
        Read/write.
    
        """
        GetDllLibPpt().ITable_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ITable_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ITable_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ITable_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets or sets the name of a shape.
        Read/write.
   
        """
        GetDllLibPpt().ITable_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ITable_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ITable_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ITable_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide of a shape.
        Read-only.
    
        """
        GetDllLibPpt().ITable_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent Presentation of the table.
        Read-only.
        """
        GetDllLibPpt().ITable_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret



    def get_Item(self ,columnIndex:int,rowIndex:int)->'Cell':
        """
        Gets the cell at the specified column and row indexes.
        Read-only 
        """
        
        GetDllLibPpt().ITable_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ITable_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Item,self.Ptr, columnIndex,rowIndex)
        ret = None if intPtr==None else Cell(intPtr)
        return ret


    def RemovePlaceholder(self):
        """
        Removes placeholder from the shape.
    
        """
        GetDllLibPpt().ITable_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ITable_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
        Dispose object and free resources.
   
        """
        GetDllLibPpt().ITable_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ITable_Dispose,self.Ptr)


    def DistributeRows(self ,startRowIndex:int,endRowIndex:int):
        """
        distribute rows.
        Args:
            startRowIndex:start row index.
            endRowIndex:end row index.
        """
        
        GetDllLibPpt().ITable_DistributeRows.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().ITable_DistributeRows,self.Ptr, startRowIndex,endRowIndex)


    def DistributeColumns(self ,startColumnIndex:int,endColumnIndex:int):
        """
        distribute columns.
        Args:
            startColumnIndex:start column index.
            endColumnIndex:end column index.
        """
        
        GetDllLibPpt().ITable_DistributeColumns.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().ITable_DistributeColumns,self.Ptr, startColumnIndex,endColumnIndex)

