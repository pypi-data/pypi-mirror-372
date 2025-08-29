from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartLegend (SpireObject) :
    """
    Represents the legend properties of a chart.
    
    This class controls the position, appearance, and content of a chart's legend.
    """
    @property
    def Width(self)->float:
        """
        Gets or sets the width of the legend.
        
        Returns:
            float: Width in points
        """
        GetDllLibPpt().ChartLegend_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().ChartLegend_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets the height of the legend.
        
        Returns:
            float: Height in points
        """
        GetDllLibPpt().ChartLegend_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().ChartLegend_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Height,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets or sets the X-coordinate of the legend.
        
        Returns:
            float: Position from left in points
        """
        GetDllLibPpt().ChartLegend_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().ChartLegend_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets the Y-coordinate of the legend.
        
        Returns:
            float: Position from top in points
        """
        GetDllLibPpt().ChartLegend_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().ChartLegend_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Top,self.Ptr, value)

    @property
    def IsOverlay(self)->bool:
        """
        Indicates whether other chart elements can overlap the legend.
        
        Returns:
            bool: True if overlapping is allowed
        """
        GetDllLibPpt().ChartLegend_get_IsOverlay.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_IsOverlay.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_IsOverlay,self.Ptr)
        return ret

    @IsOverlay.setter
    def IsOverlay(self, value:bool):
        GetDllLibPpt().ChartLegend_set_IsOverlay.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartLegend_set_IsOverlay,self.Ptr, value)

    @property

    def Position(self)->'ChartLegendPositionType':
        """
        Gets or sets the position of the legend relative to the chart.
        
        Returns:
            ChartLegendPositionType: Enum value specifying position
        """
        GetDllLibPpt().ChartLegend_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Position,self.Ptr)
        objwraped = ChartLegendPositionType(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'ChartLegendPositionType'):
        GetDllLibPpt().ChartLegend_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Position,self.Ptr, value.value)

    @property

    def Fill(self)->'FillFormat':
        """
        Gets the fill formatting properties for the legend.
        
        Returns:
            FillFormat: Object containing fill properties
        """
        GetDllLibPpt().ChartLegend_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets the line formatting properties for the legend border.
        
        Returns:
            IChartGridLine: Object containing line properties
        """
        GetDllLibPpt().ChartLegend_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets the effect properties for the legend.
        
        Returns:
            EffectDag: Object containing effect properties
        """
        GetDllLibPpt().ChartLegend_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets the 3D format properties for the legend.
        
        Returns:
            FormatThreeD: Object containing 3D properties
        """
        GetDllLibPpt().ChartLegend_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
        Gets the text formatting properties for the legend title.
        
        Returns:
            ITextFrameProperties: Object containing text properties
        """
        GetDllLibPpt().ChartLegend_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret



    def setEntrys(self ,range:'CellRanges'):
        """
        Sets the legend entries using data from specified cell ranges.
        
        Args:
            range: CellRanges object containing legend entry data
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibPpt().ChartLegend_setEntrys.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartLegend_setEntrys,self.Ptr, intPtrrange)


    def DeleteEntry(self ,index:int):
        """
        Deletes a specific legend entry.
        
        Args:
            index: The 0-based index of the entry to delete
        """
        GetDllLibPpt().ChartLegend_DeleteEntry.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ChartLegend_DeleteEntry,self.Ptr, index)

    @property

    def EntryTextProperties(self)->List['TextCharacterProperties']:
        """
        Gets text properties for individual legend entries.
        
        Returns:
            List[TextCharacterProperties]: Collection of text properties
        """
        GetDllLibPpt().ChartLegend_get_EntryTextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_EntryTextProperties.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ChartLegend_get_EntryTextProperties,self.Ptr)
        ret = GetObjVectorFromArray (intPtrArray, TextCharacterProperties)
        return ret


    @property

    def LegendEntrys(self)->'LegendEntryCollection':
        """
        Gets the collection of legend entries.
        
        Returns:
            LegendEntryCollection: Collection of legend entries
        """
        GetDllLibPpt().ChartLegend_get_LegendEntrys.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_LegendEntrys.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_LegendEntrys,self.Ptr)
        ret = None if intPtr==None else LegendEntryCollection(intPtr)
        return ret


