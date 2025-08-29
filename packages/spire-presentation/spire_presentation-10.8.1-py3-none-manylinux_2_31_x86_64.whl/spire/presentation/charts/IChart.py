from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IChart (  IShape) :
    """
    Represents a chart shape in a presentation slide.
    """
    def IsSwitchRowAndColumn(self)->bool:
        """
        Indicates whether row and column data are switched.
        """
        GetDllLibPpt().IChart_IsSwitchRowAndColumn.argtypes=[c_void_p]
        GetDllLibPpt().IChart_IsSwitchRowAndColumn.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_IsSwitchRowAndColumn,self.Ptr)
        return ret

    @property
    def PlotAreaWidthOfCalculated(self)->float:
        """
        Gets the calculated width of the plot area (read-only).
        """
        GetDllLibPpt().IChart_get_PlotAreaWidthOfCalculated.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_PlotAreaWidthOfCalculated.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IChart_get_PlotAreaWidthOfCalculated,self.Ptr)
        return ret

    @property
    def PlotVisibleCellsOnly(self)->bool:
        """
        Indicates whether only visible cells are plotted.
        """
        GetDllLibPpt().IChart_get_PlotVisibleCellsOnly.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_PlotVisibleCellsOnly.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_get_PlotVisibleCellsOnly,self.Ptr)
        return ret

    @PlotVisibleCellsOnly.setter
    def PlotVisibleCellsOnly(self, value:bool):
        GetDllLibPpt().IChart_set_PlotVisibleCellsOnly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IChart_set_PlotVisibleCellsOnly,self.Ptr, value)

    @property
    def GapDepth(self)->int:
        """
        Gets or sets the distance, as a percentage of the marker width, between the data series in a 3D chart.
            
        """
        GetDllLibPpt().IChart_get_GapDepth.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_GapDepth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChart_get_GapDepth,self.Ptr)
        return ret

    @GapDepth.setter
    def GapDepth(self, value:int):
        GetDllLibPpt().IChart_set_GapDepth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChart_set_GapDepth,self.Ptr, value)

    @property
    def BubbleScale(self)->int:
        """
        Gets or sets the BubbleScale.
        The Range of BubbleScale is 0 to 300.
    
        """
        GetDllLibPpt().IChart_get_BubbleScale.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_BubbleScale.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChart_get_BubbleScale,self.Ptr)
        return ret

    @BubbleScale.setter
    def BubbleScale(self, value:int):
        GetDllLibPpt().IChart_set_BubbleScale.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChart_set_BubbleScale,self.Ptr, value)

    @property
    def GapWidth(self)->int:
        """
        Gets or sets the space between bar or column clusters, as a percentage of the bar or column width.between 0 and 500
   
        """
        GetDllLibPpt().IChart_get_GapWidth.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_GapWidth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChart_get_GapWidth,self.Ptr)
        return ret

    @GapWidth.setter
    def GapWidth(self, value:int):
        GetDllLibPpt().IChart_set_GapWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChart_set_GapWidth,self.Ptr, value)

    @property
    def OverLap(self)->int:
        """
        Gets or sets how much bars and columns shall overlap on 2-D charts, between -100 and 100.
    
        """
        GetDllLibPpt().IChart_get_OverLap.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_OverLap.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChart_get_OverLap,self.Ptr)
        return ret

    @OverLap.setter
    def OverLap(self, value:int):
        GetDllLibPpt().IChart_set_OverLap.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChart_set_OverLap,self.Ptr, value)

    @property

    def GridLine(self)->'IChartGridLine':
        """
        Gets line style properties of a chart.
   
        """
        GetDllLibPpt().IChart_get_GridLine.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_GridLine.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_GridLine,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets effects used for a chart.
           
        """
        GetDllLibPpt().IChart_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets 3D format of a chart.
           
        """
        GetDllLibPpt().IChart_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def DisplayBlanksAs(self)->'DisplayBlanksAsType':
        """
        Gets or sets the way to plot blank cells on a chart.
            
        """
        GetDllLibPpt().IChart_get_DisplayBlanksAs.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_DisplayBlanksAs.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChart_get_DisplayBlanksAs,self.Ptr)
        objwraped = DisplayBlanksAsType(ret)
        return objwraped

    @DisplayBlanksAs.setter
    def DisplayBlanksAs(self, value:'DisplayBlanksAsType'):
        GetDllLibPpt().IChart_set_DisplayBlanksAs.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChart_set_DisplayBlanksAs,self.Ptr, value.value)

    @property

    def Series(self)->'ChartSeriesFormatCollection':
        """
        Gets chart's Series.

        """
        GetDllLibPpt().IChart_get_Series.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Series.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Series,self.Ptr)
        ret = None if intPtr==None else ChartSeriesFormatCollection(intPtr)
        return ret


    @property

    def Categories(self)->'ChartCategoryCollection':
        """
        Gets chart's Categories.

        """
        GetDllLibPpt().IChart_get_Categories.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Categories.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Categories,self.Ptr)
        ret = None if intPtr==None else ChartCategoryCollection(intPtr)
        return ret


    @property
    def HasTitle(self)->bool:
        """
        Indicates whether a chart has a visible title.
            
        """
        GetDllLibPpt().IChart_get_HasTitle.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_HasTitle.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_get_HasTitle,self.Ptr)
        return ret

    @HasTitle.setter
    def HasTitle(self, value:bool):
        GetDllLibPpt().IChart_set_HasTitle.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IChart_set_HasTitle,self.Ptr, value)

    @property
    def IsDataProtect(self)->bool:
        """
        Indicates whether data of chart is protected.
           
        """
        GetDllLibPpt().IChart_get_IsDataProtect.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_IsDataProtect.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_get_IsDataProtect,self.Ptr)
        return ret

    @IsDataProtect.setter
    def IsDataProtect(self, value:bool):
        GetDllLibPpt().IChart_set_IsDataProtect.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IChart_set_IsDataProtect,self.Ptr, value)

    @property

    def ChartTitle(self)->'ChartTextArea':
        """
        Gets or sets a chart title
    
        """
        GetDllLibPpt().IChart_get_ChartTitle.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_ChartTitle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_ChartTitle,self.Ptr)
        ret = None if intPtr==None else ChartTextArea(intPtr)
        return ret


    @property

    def ChartData(self)->'ChartData':
        """
        data associated with a chart.
    
        """
        GetDllLibPpt().IChart_get_ChartData.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_ChartData.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_ChartData,self.Ptr)
        ret = None if intPtr==None else ChartData(intPtr)
        return ret


    @property
    def HasDataTable(self)->bool:
        """
        Indicates whether a chart has a data table.
            
        """
        GetDllLibPpt().IChart_get_HasDataTable.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_HasDataTable.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_get_HasDataTable,self.Ptr)
        return ret

    @HasDataTable.setter
    def HasDataTable(self, value:bool):
        GetDllLibPpt().IChart_set_HasDataTable.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IChart_set_HasDataTable,self.Ptr, value)

    @property
    def HasLegend(self)->bool:
        """
        Indicates whether a chart has a legend.
            
        """
        GetDllLibPpt().IChart_get_HasLegend.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_HasLegend.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_get_HasLegend,self.Ptr)
        return ret

    @HasLegend.setter
    def HasLegend(self, value:bool):
        GetDllLibPpt().IChart_set_HasLegend.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IChart_set_HasLegend,self.Ptr, value)

    @property

    def ChartLegend(self)->'ChartLegend':
        """
        Gets or sets a legend for a chart.
            
        """
        GetDllLibPpt().IChart_get_ChartLegend.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_ChartLegend.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_ChartLegend,self.Ptr)
        ret = None if intPtr==None else ChartLegend(intPtr)
        return ret


    @ChartLegend.setter
    def ChartLegend(self, value:'ChartLegend'):
        GetDllLibPpt().IChart_set_ChartLegend.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IChart_set_ChartLegend,self.Ptr, value.Ptr)

    @property

    def ChartDataTable(self)->'ChartDataTable':
        """
        Gets a data table of a chart.
            
        """
        GetDllLibPpt().IChart_get_ChartDataTable.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_ChartDataTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_ChartDataTable,self.Ptr)
        ret = None if intPtr==None else ChartDataTable(intPtr)
        return ret


    @property

    def ChartStyle(self)->'ChartStyle':
        """
        Gets or sets the chart style.
            
        """
        GetDllLibPpt().IChart_get_ChartStyle.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_ChartStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChart_get_ChartStyle,self.Ptr)
        objwraped = ChartStyle(ret)
        return objwraped

    @ChartStyle.setter
    def ChartStyle(self, value:'ChartStyle'):
        GetDllLibPpt().IChart_set_ChartStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChart_set_ChartStyle,self.Ptr, value.value)

    @property

    def Type(self)->'ChartType':
        """
        Gets or sets the chart type.
            
        """
        GetDllLibPpt().IChart_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChart_get_Type,self.Ptr)
        objwraped = ChartType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'ChartType'):
        GetDllLibPpt().IChart_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChart_set_Type,self.Ptr, value.value)

    @property

    def PlotArea(self)->'ChartPlotArea':
        """
        Represents the plot area of a chart.
            
        """
        GetDllLibPpt().IChart_get_PlotArea.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_PlotArea.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_PlotArea,self.Ptr)
        ret = None if intPtr==None else ChartPlotArea(intPtr)
        return ret


    @property

    def RotationThreeD(self)->'ChartRotationThreeD':
        """
        Gets a 3D rotation of a chart.
            
        """
        GetDllLibPpt().IChart_get_RotationThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_RotationThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_RotationThreeD,self.Ptr)
        ret = None if intPtr==None else ChartRotationThreeD(intPtr)
        return ret


    @property

    def BackWall(self)->'ChartWallsOrFloor':
        """
        Gets the back wall of a 3D chart.
            
        """
        GetDllLibPpt().IChart_get_BackWall.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_BackWall.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_BackWall,self.Ptr)
        ret = None if intPtr==None else ChartWallsOrFloor(intPtr)
        return ret


    @property

    def SideWall(self)->'ChartWallsOrFloor':
        """
        Gets the side wall of a 3D chart.
            
        """
        GetDllLibPpt().IChart_get_SideWall.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_SideWall.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_SideWall,self.Ptr)
        ret = None if intPtr==None else ChartWallsOrFloor(intPtr)
        return ret


    @property

    def Floor(self)->'ChartWallsOrFloor':
        """
        Gets the floor of a 3D chart.
            
        """
        GetDllLibPpt().IChart_get_Floor.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Floor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Floor,self.Ptr)
        ret = None if intPtr==None else ChartWallsOrFloor(intPtr)
        return ret


    @property

    def PrimaryCategoryAxis(self)->'IChartAxis':
        """
         Gets the chart's Category axis
        """
        GetDllLibPpt().IChart_get_PrimaryCategoryAxis.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_PrimaryCategoryAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_PrimaryCategoryAxis,self.Ptr)
        ret = None if intPtr==None else IChartAxis(intPtr)
        return ret


    @property

    def SecondaryCategoryAxis(self)->'IChartAxis':
        """
         Gets the chart's second Category axis.

        """
        GetDllLibPpt().IChart_get_SecondaryCategoryAxis.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_SecondaryCategoryAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_SecondaryCategoryAxis,self.Ptr)
        ret = None if intPtr==None else IChartAxis(intPtr)
        return ret


    @property

    def PrimaryValueAxis(self)->'IChartAxis':
        """
         Gets the chart's Value axis.
     
        """
        GetDllLibPpt().IChart_get_PrimaryValueAxis.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_PrimaryValueAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_PrimaryValueAxis,self.Ptr)
        ret = None if intPtr==None else IChartAxis(intPtr)
        return ret


    @property

    def SecondaryValueAxis(self)->'IChartAxis':
        """
         Gets the chart's second Value axis.
     
        """
        GetDllLibPpt().IChart_get_SecondaryValueAxis.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_SecondaryValueAxis.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_SecondaryValueAxis,self.Ptr)
        ret = None if intPtr==None else IChartAxis(intPtr)
        return ret


    @property

    def ShapeLocking(self)->'GraphicalNodeLocking':
        """
        Gets lock type of shape.

        """
        GetDllLibPpt().IChart_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else GraphicalNodeLocking(intPtr)
        return ret


    @property
    def IsPlaceholder(self)->bool:
        """
        Indicates whether the shape is Placeholder.
    
        """
        GetDllLibPpt().IChart_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_get_IsPlaceholder,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
        Gets the placeholder for a shape.
    
        """
        GetDllLibPpt().IChart_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the shape's tags collection.
    
        """
        GetDllLibPpt().IChart_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets or sets the shape frame's properties.
    
        """
        GetDllLibPpt().IChart_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().IChart_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IChart_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets the LineFormat object that contains line formatting properties for a shape.
        Note: can return null for certain types of shapes which don't have line properties.
    
        """
        GetDllLibPpt().IChart_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
        Gets the ThreeDFormat object that 3d effect properties for a shape.
        Note: can return null for certain types of shapes which don't have 3d properties.
    
        """
        GetDllLibPpt().IChart_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets the EffectFormat object which contains pixel effects applied to a shape.
        Note: can return null for certain types of shapes which don't have effect properties.
    
        """
        GetDllLibPpt().IChart_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets the FillFormat object that contains fill formatting properties for a shape.
        Note: can return null for certain types of shapes which don't have fill properties.
    
        """
        GetDllLibPpt().IChart_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink defined for mouse click.
    
        """
        GetDllLibPpt().IChart_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().IChart_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IChart_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink defined for mouse over.
    
        """
        GetDllLibPpt().IChart_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().IChart_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IChart_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
        Indicates whether the shape is hidden.
    
        """
        GetDllLibPpt().IChart_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().IChart_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IChart_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
        Gets the parent slide of a shape.
    
        """
        GetDllLibPpt().IChart_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
        Gets or sets the position of a shape in the z-order.
        Shapes[0] returns the shape at the back of the z-order,
        and Shapes[Shapes.Count - 1] returns the shape at the front of the z-order.
    
        """
        GetDllLibPpt().IChart_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IChart_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().IChart_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IChart_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
        Gets or sets the number of degrees the specified shape is rotated around
        the z-axis. A positive value indicates clockwise rotation; a negative value
        indicates counterclockwise rotation.
    
        """
        GetDllLibPpt().IChart_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IChart_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().IChart_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IChart_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets or sets the x-coordinate of the upper-left corner of the shape.
    
        """
        GetDllLibPpt().IChart_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IChart_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().IChart_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IChart_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets the y-coordinate of the upper-left corner of the shape.
    
        """
        GetDllLibPpt().IChart_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IChart_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().IChart_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IChart_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets the width of the shape.
    
        """
        GetDllLibPpt().IChart_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IChart_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().IChart_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IChart_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets the height of the shape.
    
        """
        GetDllLibPpt().IChart_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IChart_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().IChart_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IChart_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
        Gets or sets the alternative text associated with a shape.
    
        """
        GetDllLibPpt().IChart_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IChart_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IChart_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IChart_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets or sets the name of a shape.
    
        """
        GetDllLibPpt().IChart_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IChart_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IChart_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IChart_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide of a shape.
    
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IChart_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Get the presentation.
        """
        GetDllLibPpt().IChart_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    def RemovePlaceholder(self):
        """
        Removes placeholder from the shape.
    
        """
        GetDllLibPpt().IChart_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IChart_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
        Dispose object and free resources.
    
        """
        GetDllLibPpt().IChart_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IChart_Dispose,self.Ptr)

    @property
    def BorderRoundedCorners(self)->bool:
        """
        Get or set the chart border if rounded corners.
    
        """
        GetDllLibPpt().IChart_get_BorderRoundedCorners.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_BorderRoundedCorners.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IChart_get_BorderRoundedCorners,self.Ptr)
        return ret

    @BorderRoundedCorners.setter
    def BorderRoundedCorners(self, value:bool):
        GetDllLibPpt().IChart_set_BorderRoundedCorners.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IChart_set_BorderRoundedCorners,self.Ptr, value)

    @property

    def SeriesLine(self)->'TextLineFormat':
        """
        Get the chart series line format
    
        """
        GetDllLibPpt().IChart_get_SeriesLine.argtypes=[c_void_p]
        GetDllLibPpt().IChart_get_SeriesLine.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChart_get_SeriesLine,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    def SwitchRowAndColumn(self):
        """
        Switch Row And Column
    
        """
        GetDllLibPpt().IChart_SwitchRowAndColumn.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IChart_SwitchRowAndColumn,self.Ptr)

