from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Cell (  IActiveSlide, IActivePresentation) :
    """
    Represents a single cell in a presentation table.
    Provides properties for layout, formatting, and content management.
    """
    @property
    def OffsetX(self)->float:
        """
        Gets the horizontal offset from table's left edge to cell's left edge.
        Read-only.
        
        Returns:
            float: Horizontal offset in points.
        """
        GetDllLibPpt().Cell_get_OffsetX.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_OffsetX.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_OffsetX,self.Ptr)
        return ret

    @property
    def OffsetY(self)->float:
        """
        Gets the vertical offset from table's top edge to cell's top edge.
        Read-only.
        
        Returns:
            float: Vertical offset in points.
        """
        GetDllLibPpt().Cell_get_OffsetY.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_OffsetY.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_OffsetY,self.Ptr)
        return ret

    @property
    def FirstRowIndex(self)->int:
        """
        Gets the index of the first row spanned by this cell.
        Read-only.
        
        Returns:
            int: First row index.
        """
        GetDllLibPpt().Cell_get_FirstRowIndex.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_FirstRowIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_FirstRowIndex,self.Ptr)
        return ret

    @property
    def FirstColumnIndex(self)->int:
        """
        Gets an index of first column, covered by the cell.
        Returns:
            int: First column index.
        """
        GetDllLibPpt().Cell_get_FirstColumnIndex.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_FirstColumnIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_FirstColumnIndex,self.Ptr)
        return ret

    @property
    def Width(self)->float:
        """
        Gets the width of the cell.
            
        """
        GetDllLibPpt().Cell_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_Width,self.Ptr)
        return ret

    @property
    def Height(self)->float:
        """
        Gets the height of the cell.
           
        """
        GetDllLibPpt().Cell_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_Height.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_Height,self.Ptr)
        return ret

    @property
    def MinimalHeight(self)->float:
        """
        Gets the minimum height of a cell.
        This is a sum of minimal heights of all rows cowered by the cell.
            
        """
        GetDllLibPpt().Cell_get_MinimalHeight.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MinimalHeight.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MinimalHeight,self.Ptr)
        return ret

    @property

    def BorderLeft(self)->'TextLineFormat':
        """
        Gets a left border line properties object.
        Read-only 
        """
        GetDllLibPpt().Cell_get_BorderLeft.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderLeft.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderLeft,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderTop(self)->'TextLineFormat':
        """
        Gets a top border line properties object.
        Read-only
        """
        GetDllLibPpt().Cell_get_BorderTop.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderTop.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderTop,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderRight(self)->'TextLineFormat':
        """
        Gets a right border line properties object.
        Read-only 
        """
        GetDllLibPpt().Cell_get_BorderRight.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderRight.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderRight,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderBottom(self)->'TextLineFormat':
        """
        Gets a bottom border line properties object.
        Read-only 
        """
        GetDllLibPpt().Cell_get_BorderBottom.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderBottom.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderBottom,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderLeftDisplayColor(self)->'Color':
        """
        Gets a left border display color.
    
        """
        GetDllLibPpt().Cell_get_BorderLeftDisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderLeftDisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderLeftDisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def BorderTopDisplayColor(self)->'Color':
        """
        Gets a top border display color.
    
        """
        GetDllLibPpt().Cell_get_BorderTopDisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderTopDisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderTopDisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def BorderRightDisplayColor(self)->'Color':
        """
        Gets a right border display color.
    
        """
        GetDllLibPpt().Cell_get_BorderRightDisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderRightDisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderRightDisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def BorderBottomDisplayColor(self)->'Color':
        """
        Gets a bottom border display color.
    
        """
        GetDllLibPpt().Cell_get_BorderBottomDisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderBottomDisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderBottomDisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def BorderDiagonalDown(self)->'TextLineFormat':
        """
        Gets a top-left to bottom-right diagonal line properties object.
        Read-only 
        """
        GetDllLibPpt().Cell_get_BorderDiagonalDown.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderDiagonalDown.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderDiagonalDown,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderDiagonalUp(self)->'TextLineFormat':
        """
        Gets a bottom-left to top-right diagonal line properties object.
        Read-only 
        """
        GetDllLibPpt().Cell_get_BorderDiagonalUp.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderDiagonalUp.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderDiagonalUp,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def FillFormat(self)->'FillFormat':
        """
        Gets a cell fill properties object.
        Read-only
        """
        GetDllLibPpt().Cell_get_FillFormat.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_FillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_FillFormat,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property
    def MarginLeft(self)->float:
        """
        Gets or sets the left margin in a TextFrame.
        Read/write 
        """
        GetDllLibPpt().Cell_get_MarginLeft.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MarginLeft.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MarginLeft,self.Ptr)
        return ret

    @MarginLeft.setter
    def MarginLeft(self, value:float):
        GetDllLibPpt().Cell_set_MarginLeft.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().Cell_set_MarginLeft,self.Ptr, value)

    @property
    def MarginRight(self)->float:
        """
        Gets or sets the right margin in a TextFrame.
        Read/write 
        """
        GetDllLibPpt().Cell_get_MarginRight.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MarginRight.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MarginRight,self.Ptr)
        return ret

    @MarginRight.setter
    def MarginRight(self, value:float):
        GetDllLibPpt().Cell_set_MarginRight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().Cell_set_MarginRight,self.Ptr, value)

    @property
    def MarginTop(self)->float:
        """
        Gets or sets the top margin in a TextFrame.
        Read/write 
        """
        GetDllLibPpt().Cell_get_MarginTop.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MarginTop.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MarginTop,self.Ptr)
        return ret

    @MarginTop.setter
    def MarginTop(self, value:float):
        GetDllLibPpt().Cell_set_MarginTop.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().Cell_set_MarginTop,self.Ptr, value)

    @property
    def MarginBottom(self)->float:
        """
        Gets or sets the bottom margin in a TextFrame.
        Read/write
        """
        GetDllLibPpt().Cell_get_MarginBottom.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MarginBottom.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MarginBottom,self.Ptr)
        return ret

    @MarginBottom.setter
    def MarginBottom(self, value:float):
        GetDllLibPpt().Cell_set_MarginBottom.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().Cell_set_MarginBottom,self.Ptr, value)

    @property

    def VerticalTextType(self)->'VerticalTextType':
        """
        Gets or sets the type of vertical text.
        Read/write 
        """
        GetDllLibPpt().Cell_get_VerticalTextType.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_VerticalTextType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_VerticalTextType,self.Ptr)
        objwraped = VerticalTextType(ret)
        return objwraped

    @VerticalTextType.setter
    def VerticalTextType(self, value:'VerticalTextType'):
        GetDllLibPpt().Cell_set_VerticalTextType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Cell_set_VerticalTextType,self.Ptr, value.value)

    @property

    def TextAnchorType(self)->'TextAnchorType':
        """
        Gets or sets the text anchor type.
        Read/write 
        """
        GetDllLibPpt().Cell_get_TextAnchorType.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_TextAnchorType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_TextAnchorType,self.Ptr)
        objwraped = TextAnchorType(ret)
        return objwraped

    @TextAnchorType.setter
    def TextAnchorType(self, value:'TextAnchorType'):
        GetDllLibPpt().Cell_set_TextAnchorType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Cell_set_TextAnchorType,self.Ptr, value.value)

    @property
    def AnchorCenter(self)->bool:
        """
        Indicates whether or not text box centered inside a cell.
        Read/write 
        """
        GetDllLibPpt().Cell_get_AnchorCenter.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_AnchorCenter.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Cell_get_AnchorCenter,self.Ptr)
        return ret

    @AnchorCenter.setter
    def AnchorCenter(self, value:bool):
        GetDllLibPpt().Cell_set_AnchorCenter.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Cell_set_AnchorCenter,self.Ptr, value)

    @property
    def ColSpan(self)->int:
        """
        Gets the number of grid columns in the parent table's table grid
        which shall be spanned by the current cell. This property allows cells
        to have the appearance of being merged, as they span vertical boundaries
        of other cells in the table.
        Read-only 
        """
        GetDllLibPpt().Cell_get_ColSpan.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_ColSpan.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_ColSpan,self.Ptr)
        return ret

    @property
    def RowSpan(self)->int:
        """
        Gets the number of rows that a merged cell spans. This is used in combination
        with the vMerge attribute on other cells in order to specify the beginning cell
        of a horizontal merge.
        Read-only.
        """
        GetDllLibPpt().Cell_get_RowSpan.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_RowSpan.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_RowSpan,self.Ptr)
        return ret

    @property

    def TextFrame(self)->'ITextFrameProperties':
        """
        Gets the text frame of a cell.
        Read-only 
        """
        GetDllLibPpt().Cell_get_TextFrame.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_TextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide of a cell.
        Read-only 
        """
        GetDllLibPpt().Cell_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation of a cell.
        Read-only 
        """
        from spire.presentation import Presentation
        GetDllLibPpt().Cell_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret



    def Split(self ,RowCount:int,ColunmCount:int):
        """
        Split the cell.
        Args:
            RowCount:The number of cells being split in the row direction.
            ColunmCount:The number of cells being split in the colunm direction.
        """
        
        GetDllLibPpt().Cell_Split.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().Cell_Split,self.Ptr, RowCount,ColunmCount)

    def SplitBySpan(self):
        """
        The cell is split into its RowSpan rows in the  row direction,
        and it is split into its ColSpan colunms in the colunm direction.
        """
        GetDllLibPpt().Cell_SplitBySpan.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Cell_SplitBySpan,self.Ptr)

    @property

    def DisplayColor(self)->'Color':
        """
        get cell's display color
   
        """
        GetDllLibPpt().Cell_get_DisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_DisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_DisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


