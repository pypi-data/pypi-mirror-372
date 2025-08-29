from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartAxis (  PptObject, IChartAxis) :
    """
    Represents a chart axis, defining scale, labels, and formatting for chart dimensions.
    
    This class provides comprehensive control over axis properties including scaling, 
    tick marks, grid lines, labels, and positioning for both category and value axes.
    """
    @property
    def IsCrossCategories(self)->bool:
        """
        Indicates whether the value axis crosses between categories.
        
        Returns:
            bool: True if crossing between categories, False otherwise
        """
        GetDllLibPpt().ChartAxis_get_IsCrossCategories.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsCrossCategories.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsCrossCategories,self.Ptr)
        return ret

    @IsCrossCategories.setter
    def IsCrossCategories(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsCrossCategories.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsCrossCategories,self.Ptr, value)

    @property
    def CrossAt(self)->float:
        """
        Gets or sets the point where the category axis crosses the value axis.
        
        Returns:
            float: The crossing point value
        """
        GetDllLibPpt().ChartAxis_get_CrossAt.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_CrossAt.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_CrossAt,self.Ptr)
        return ret

    @CrossAt.setter
    def CrossAt(self, value:float):
        GetDllLibPpt().ChartAxis_set_CrossAt.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartAxis_set_CrossAt,self.Ptr, value)

    @property

    def DisplayUnit(self)->'ChartDisplayUnitType':
        """
        Gets or sets the unit label for the axis.
        
        Returns:
            ChartDisplayUnitType: The current display unit type
        """
        GetDllLibPpt().ChartAxis_get_DisplayUnit.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_DisplayUnit.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_DisplayUnit,self.Ptr)
        objwraped = ChartDisplayUnitType(ret)
        return objwraped

    @DisplayUnit.setter
    def DisplayUnit(self, value:'ChartDisplayUnitType'):
        GetDllLibPpt().ChartAxis_set_DisplayUnit.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_DisplayUnit,self.Ptr, value.value)

    @property
    def IsAutoMax(self)->bool:
        """
        Indicates whether the axis maximum is automatically calculated.
        
        Returns:
            bool: True if maximum is automatic, False if manually specified
        """
        GetDllLibPpt().ChartAxis_get_IsAutoMax.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsAutoMax.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsAutoMax,self.Ptr)
        return ret

    @IsAutoMax.setter
    def IsAutoMax(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsAutoMax.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsAutoMax,self.Ptr, value)

    @property
    def MaxValue(self)->float:
        """
        Gets or sets the maximum value for the axis.
        
        Returns:
            float: The maximum axis value
        """
        GetDllLibPpt().ChartAxis_get_MaxValue.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MaxValue.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_MaxValue,self.Ptr)
        return ret

    @MaxValue.setter
    def MaxValue(self, value:float):
        GetDllLibPpt().ChartAxis_set_MaxValue.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartAxis_set_MaxValue,self.Ptr, value)

    @property
    def MinorUnit(self)->float:
        """
        Gets or sets value of minor increment.
        
        Returns:
            float: The minor increment.
        """
        GetDllLibPpt().ChartAxis_get_MinorUnit.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MinorUnit.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_MinorUnit,self.Ptr)
        return ret

    @MinorUnit.setter
    def MinorUnit(self, value:float):
        GetDllLibPpt().ChartAxis_set_MinorUnit.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartAxis_set_MinorUnit,self.Ptr, value)

    @property
    def IsAutoMinor(self)->bool:
        """
        Gets or sets Indicates whether the minor unit of the axis is automatically assigned.
        
        Returns:
            bool: if the minor unit of the axis is automatically assigned.
        """
        GetDllLibPpt().ChartAxis_get_IsAutoMinor.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsAutoMinor.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsAutoMinor,self.Ptr)
        return ret

    @IsAutoMinor.setter
    def IsAutoMinor(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsAutoMinor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsAutoMinor,self.Ptr, value)

    @property
    def MajorUnit(self)->float:
        """
        Gets or sets the major units for the axis.
        
        Returns:
            float: The major units value.
        """
        GetDllLibPpt().ChartAxis_get_MajorUnit.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MajorUnit.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_MajorUnit,self.Ptr)
        return ret

    @MajorUnit.setter
    def MajorUnit(self, value:float):
        GetDllLibPpt().ChartAxis_set_MajorUnit.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartAxis_set_MajorUnit,self.Ptr, value)

    @property
    def IsAutoMajor(self)->bool:
        """
        Gets or sets automatic major selected. 
        
        Returns:
            bool: if major unit is automatic.
        """
        GetDllLibPpt().ChartAxis_get_IsAutoMajor.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsAutoMajor.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsAutoMajor,self.Ptr)
        return ret

    @IsAutoMajor.setter
    def IsAutoMajor(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsAutoMajor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsAutoMajor,self.Ptr, value)

    @property
    def IsAutoMin(self)->bool:
        """
        Gets or sets automatic min selected. 
        
        Returns:
            bool: if min unit is automatic.
        """
        GetDllLibPpt().ChartAxis_get_IsAutoMin.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsAutoMin.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsAutoMin,self.Ptr)
        return ret

    @IsAutoMin.setter
    def IsAutoMin(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsAutoMin.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsAutoMin,self.Ptr, value)

    @property
    def MinValue(self)->float:
        """
        Represents the minimum value on the value axis.
        
        Returns:
            float: minimum value.
        """
        GetDllLibPpt().ChartAxis_get_MinValue.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MinValue.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_MinValue,self.Ptr)
        return ret

    @MinValue.setter
    def MinValue(self, value:float):
        GetDllLibPpt().ChartAxis_set_MinValue.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartAxis_set_MinValue,self.Ptr, value)

    @property
    def IsLogScale(self)->bool:
        """
        Logarithmic scale.
        
        Returns:
            bool: if Logarithmic scale.
        """
        GetDllLibPpt().ChartAxis_get_IsLogScale.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsLogScale.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsLogScale,self.Ptr)
        return ret

    @IsLogScale.setter
    def IsLogScale(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsLogScale.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsLogScale,self.Ptr, value)

    @property
    def LogScale(self)->int:
        """
        Gets or sets the logarithmic base.
        
        Returns:
            int: logarithmic base.
        """
        GetDllLibPpt().ChartAxis_get_LogScale.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_LogScale.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_LogScale,self.Ptr)
        return ret

    @LogScale.setter
    def LogScale(self, value:int):
        GetDllLibPpt().ChartAxis_set_LogScale.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_LogScale,self.Ptr, value)

    @property
    def IsReversed(self)->bool:
        """
        Gets or set plots data points from last to first.
        
        Returns:
            bool:if plots data points are from last to first.
        """
        GetDllLibPpt().ChartAxis_get_IsReversed.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsReversed.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsReversed,self.Ptr)
        return ret

    @IsReversed.setter
    def IsReversed(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsReversed.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsReversed,self.Ptr, value)

    @property
    def IsVisible(self)->bool:
        """
        Gets or sets if the axis is visible.
        """
        GetDllLibPpt().ChartAxis_get_IsVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsVisible,self.Ptr)
        return ret

    @IsVisible.setter
    def IsVisible(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsVisible,self.Ptr, value)

    @property

    def MajorTickMark(self)->'TickMarkType':
        """
        Represents major tick marks.
        
        Returns:
            TickMarkType:TickMark Type.
        """
        GetDllLibPpt().ChartAxis_get_MajorTickMark.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MajorTickMark.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_MajorTickMark,self.Ptr)
        objwraped = TickMarkType(ret)
        return objwraped

    @MajorTickMark.setter
    def MajorTickMark(self, value:'TickMarkType'):
        GetDllLibPpt().ChartAxis_set_MajorTickMark.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_MajorTickMark,self.Ptr, value.value)

    @property

    def MinorTickMark(self)->'TickMarkType':
        """
        Represents the type of minor tick mark for the specified axis.
        """
        GetDllLibPpt().ChartAxis_get_MinorTickMark.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MinorTickMark.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_MinorTickMark,self.Ptr)
        objwraped = TickMarkType(ret)
        return objwraped

    @MinorTickMark.setter
    def MinorTickMark(self, value:'TickMarkType'):
        GetDllLibPpt().ChartAxis_set_MinorTickMark.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_MinorTickMark,self.Ptr, value.value)

    @property

    def TickLabelPosition(self)->'TickLabelPositionType':
        """
        Represents the position of tick-mark labels on the specified axis.
        """
        GetDllLibPpt().ChartAxis_get_TickLabelPosition.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_TickLabelPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_TickLabelPosition,self.Ptr)
        objwraped = TickLabelPositionType(ret)
        return objwraped

    @TickLabelPosition.setter
    def TickLabelPosition(self, value:'TickLabelPositionType'):
        GetDllLibPpt().ChartAxis_set_TickLabelPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_TickLabelPosition,self.Ptr, value.value)

    @property

    def MajorUnitScale(self)->'ChartBaseUnitType':
        
        """
        Represents the major unit scale for the category axis.
  
        """
        GetDllLibPpt().ChartAxis_get_MajorUnitScale.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MajorUnitScale.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_MajorUnitScale,self.Ptr)
        objwraped = ChartBaseUnitType(ret)
        return objwraped

    @MajorUnitScale.setter
    def MajorUnitScale(self, value:'ChartBaseUnitType'):
        GetDllLibPpt().ChartAxis_set_MajorUnitScale.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_MajorUnitScale,self.Ptr, value.value)

    @property

    def MinorUnitScale(self)->'ChartBaseUnitType':
        """
         Represents the major unit scale for the category axis.

        """
        GetDllLibPpt().ChartAxis_get_MinorUnitScale.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MinorUnitScale.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_MinorUnitScale,self.Ptr)
        objwraped = ChartBaseUnitType(ret)
        return objwraped

    @MinorUnitScale.setter
    def MinorUnitScale(self, value:'ChartBaseUnitType'):
        GetDllLibPpt().ChartAxis_set_MinorUnitScale.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_MinorUnitScale,self.Ptr, value.value)

    @property

    def BaseUnitScale(self)->'ChartBaseUnitType':
        """
         Represents the base unit scale for the category axis.
     
        """
        GetDllLibPpt().ChartAxis_get_BaseUnitScale.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_BaseUnitScale.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_BaseUnitScale,self.Ptr)
        objwraped = ChartBaseUnitType(ret)
        return objwraped

    @BaseUnitScale.setter
    def BaseUnitScale(self, value:'ChartBaseUnitType'):
        GetDllLibPpt().ChartAxis_set_BaseUnitScale.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_BaseUnitScale,self.Ptr, value.value)

    @property

    def MinorGridLines(self)->'IChartGridLine':
        """
        Represents minor gridlines on a chart axis.

        """
        GetDllLibPpt().ChartAxis_get_MinorGridLines.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MinorGridLines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartAxis_get_MinorGridLines,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def MajorGridTextLines(self)->'IChartGridLine':
        """
        Represents major gridlines on a chart axis.
    
        """
        GetDllLibPpt().ChartAxis_get_MajorGridTextLines.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_MajorGridTextLines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartAxis_get_MajorGridTextLines,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def ChartEffectFormat(self)->'IChartEffectFormat':
        """
        Represents format of axis.

        """
        GetDllLibPpt().ChartAxis_get_ChartEffectFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_ChartEffectFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartAxis_get_ChartEffectFormat,self.Ptr)
        ret = None if intPtr==None else IChartEffectFormat(intPtr)
        return ret


    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
        Represent text properties of axis
   
        """
        GetDllLibPpt().ChartAxis_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartAxis_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Title(self)->'ChartTextArea':
        """
        Gets the axis' title.
     
        """
        GetDllLibPpt().ChartAxis_get_Title.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_Title.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartAxis_get_Title,self.Ptr)
        ret = None if intPtr==None else ChartTextArea(intPtr)
        return ret


    @property

    def ChartCrossType(self)->'ChartCrossesType':
        """
         Represents the CrossType on the specified axis where the other axis crosses.
    
        """
        GetDllLibPpt().ChartAxis_get_ChartCrossType.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_ChartCrossType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_ChartCrossType,self.Ptr)
        objwraped = ChartCrossesType(ret)
        return objwraped

    @ChartCrossType.setter
    def ChartCrossType(self, value:'ChartCrossesType'):
        GetDllLibPpt().ChartAxis_set_ChartCrossType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_ChartCrossType,self.Ptr, value.value)

    @property

    def Position(self)->'AxisPositionType':
        """
        Represents position of axis
   
        """
        GetDllLibPpt().ChartAxis_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_Position,self.Ptr)
        objwraped = AxisPositionType(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'AxisPositionType'):
        GetDllLibPpt().ChartAxis_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_Position,self.Ptr, value.value)

    @property
    def HasTitle(self)->bool:
        """
        Indicates whether a axis has a visible title.
   
        """
        GetDllLibPpt().ChartAxis_get_HasTitle.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_HasTitle.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_HasTitle,self.Ptr)
        return ret

    @HasTitle.setter
    def HasTitle(self, value:bool):
        GetDllLibPpt().ChartAxis_set_HasTitle.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_HasTitle,self.Ptr, value)

    @property

    def CrossBetweenType(self)->'CrossBetweenType':
        """

        """
        GetDllLibPpt().ChartAxis_get_CrossBetweenType.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_CrossBetweenType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_CrossBetweenType,self.Ptr)
        objwraped = CrossBetweenType(ret)
        return objwraped

    @CrossBetweenType.setter
    def CrossBetweenType(self, value:'CrossBetweenType'):
        GetDllLibPpt().ChartAxis_set_CrossBetweenType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_CrossBetweenType,self.Ptr, value.value)

    @property

    def NumberFormat(self)->str:
        """
        Gets or sets number format string.
    
        """
        GetDllLibPpt().ChartAxis_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartAxis_get_NumberFormat,self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartAxis_set_NumberFormat.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartAxis_set_NumberFormat,self.Ptr,valuePtr)

    @property
    def HasDataSource(self)->bool:
        """
        Indicates whether the format is linked source data.

        """
        GetDllLibPpt().ChartAxis_get_HasDataSource.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_HasDataSource.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_HasDataSource,self.Ptr)
        return ret

    @HasDataSource.setter
    def HasDataSource(self, value:bool):
        GetDllLibPpt().ChartAxis_set_HasDataSource.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_HasDataSource,self.Ptr, value)

    @property
    def TextRotationAngle(self)->float:
        """
        Text rotation angle.

        """
        GetDllLibPpt().ChartAxis_get_TextRotationAngle.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_TextRotationAngle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_TextRotationAngle,self.Ptr)
        return ret

    @TextRotationAngle.setter
    def TextRotationAngle(self, value:float):
        GetDllLibPpt().ChartAxis_set_TextRotationAngle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartAxis_set_TextRotationAngle,self.Ptr, value)

    @property

    def TickLabelSpacing(self)->'UInt32':
        """
        Represents the number of categories or series between tick-mark labels.

        """
        GetDllLibPpt().ChartAxis_get_TickLabelSpacing.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_TickLabelSpacing.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartAxis_get_TickLabelSpacing,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret


    @TickLabelSpacing.setter
    def TickLabelSpacing(self, value:'UInt32'):
        GetDllLibPpt().ChartAxis_set_TickLabelSpacing.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartAxis_set_TickLabelSpacing,self.Ptr, value.Ptr)

    @property
    def IsAutomaticTickLabelSpacing(self)->bool:
        """
        Indicates whether tick label spacing is automatic.
        """
        GetDllLibPpt().ChartAxis_get_IsAutomaticTickLabelSpacing.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsAutomaticTickLabelSpacing.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsAutomaticTickLabelSpacing,self.Ptr)
        return ret

    @IsAutomaticTickLabelSpacing.setter
    def IsAutomaticTickLabelSpacing(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsAutomaticTickLabelSpacing.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsAutomaticTickLabelSpacing,self.Ptr, value)

    @property

    def TickMarkSpacing(self)->'UInt32':
        """
        Represents the number of ticks between tick-mark labels.

        """
        GetDllLibPpt().ChartAxis_get_TickMarkSpacing.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_TickMarkSpacing.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartAxis_get_TickMarkSpacing,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret


    @TickMarkSpacing.setter
    def TickMarkSpacing(self, value:'UInt32'):
        GetDllLibPpt().ChartAxis_set_TickMarkSpacing.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartAxis_set_TickMarkSpacing,self.Ptr, value.Ptr)

    @property
    def IsAutomaticTickMarkSpacing(self)->bool:
        """

        """
        GetDllLibPpt().ChartAxis_get_IsAutomaticTickMarkSpacing.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsAutomaticTickMarkSpacing.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsAutomaticTickMarkSpacing,self.Ptr)
        return ret

    @IsAutomaticTickMarkSpacing.setter
    def IsAutomaticTickMarkSpacing(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsAutomaticTickMarkSpacing.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsAutomaticTickMarkSpacing,self.Ptr, value)

    @property
    def LblOffset(self)->int:
        """
        Represents the distance between tick-mark labels and axis.

        """
        GetDllLibPpt().ChartAxis_get_LblOffset.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_LblOffset.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_LblOffset,self.Ptr)
        return ret

    @property
    def HasMultiLvlLbl(self)->bool:
        """
        Gets or sets if the label of categoryAxis has multiple levels.

        """
        GetDllLibPpt().ChartAxis_get_HasMultiLvlLbl.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_HasMultiLvlLbl.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_HasMultiLvlLbl,self.Ptr)
        return ret

    @HasMultiLvlLbl.setter
    def HasMultiLvlLbl(self, value:bool):
        GetDllLibPpt().ChartAxis_set_HasMultiLvlLbl.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_HasMultiLvlLbl,self.Ptr, value)

    @property
    def IsMergeSameLabel(self)->bool:
        """
        Gets or sets if the first level label of categoryAxis merge the same item.
   
        """
        GetDllLibPpt().ChartAxis_get_IsMergeSameLabel.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsMergeSameLabel.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsMergeSameLabel,self.Ptr)
        return ret

    @IsMergeSameLabel.setter
    def IsMergeSameLabel(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsMergeSameLabel.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsMergeSameLabel,self.Ptr, value)

    @property

    def AxisType(self)->'AxisType':
        """
        Axis type.
        """
        GetDllLibPpt().ChartAxis_get_AxisType.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_AxisType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_AxisType,self.Ptr)
        objwraped = AxisType(ret)
        return objwraped

    @AxisType.setter
    def AxisType(self, value:'AxisType'):
        GetDllLibPpt().ChartAxis_set_AxisType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_AxisType,self.Ptr, value.value)

    @property
    def IsBinningByCategory(self)->bool:
        """
        True if bins generated by category values. otherwise False
    
        """
        GetDllLibPpt().ChartAxis_get_IsBinningByCategory.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_IsBinningByCategory.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_IsBinningByCategory,self.Ptr)
        return ret

    @IsBinningByCategory.setter
    def IsBinningByCategory(self, value:bool):
        GetDllLibPpt().ChartAxis_set_IsBinningByCategory.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_IsBinningByCategory,self.Ptr, value)

    @property
    def HasAutomaticBins(self)->bool:
        """
    
        True if bins generated are automatic. otherwise False
        Applies only to Histogram and Pareto charts.

        """
        GetDllLibPpt().ChartAxis_get_HasAutomaticBins.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_HasAutomaticBins.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_HasAutomaticBins,self.Ptr)
        return ret

    @HasAutomaticBins.setter
    def HasAutomaticBins(self, value:bool):
        GetDllLibPpt().ChartAxis_set_HasAutomaticBins.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartAxis_set_HasAutomaticBins,self.Ptr, value)

    @property
    def NumberOfBins(self)->int:
        """
        Get or set the Number of Bins in the axis
    
        Applies only to Histogram and Pareto charts.Can be a value from 1 through 31999.

        """
        GetDllLibPpt().ChartAxis_get_NumberOfBins.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_NumberOfBins.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_NumberOfBins,self.Ptr)
        return ret

    @NumberOfBins.setter
    def NumberOfBins(self, value:int):
        GetDllLibPpt().ChartAxis_set_NumberOfBins.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_NumberOfBins,self.Ptr, value)

    @property
    def BinWidth(self)->float:
        """
        Get or Set the number of data points in each range.
   
        Applies only to Histogram and Pareto charts.
        """
        GetDllLibPpt().ChartAxis_get_BinWidth.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_BinWidth.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_BinWidth,self.Ptr)
        return ret

    @BinWidth.setter
    def BinWidth(self, value:float):
        GetDllLibPpt().ChartAxis_set_BinWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ChartAxis_set_BinWidth,self.Ptr, value)

    @property
    def UnderflowBinValue(self)->float:
        """
        Get or Set the UnderFlow Bin value
        Applies only to Histogram and Pareto charts.

        """
        GetDllLibPpt().ChartAxis_get_UnderflowBinValue.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_UnderflowBinValue.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_UnderflowBinValue,self.Ptr)
        return ret

    @UnderflowBinValue.setter
    def UnderflowBinValue(self, value:float):
        GetDllLibPpt().ChartAxis_set_UnderflowBinValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ChartAxis_set_UnderflowBinValue,self.Ptr, value)

    @property
    def OverflowBinValue(self)->float:
        """
        Get or Set the OverFlow Bin value
        Applies only to Histogram and Pareto charts.
        """
        GetDllLibPpt().ChartAxis_get_OverflowBinValue.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_OverflowBinValue.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_OverflowBinValue,self.Ptr)
        return ret

    @OverflowBinValue.setter
    def OverflowBinValue(self, value:float):
        GetDllLibPpt().ChartAxis_set_OverflowBinValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ChartAxis_set_OverflowBinValue,self.Ptr, value)

    @property
    def GapWidth(self)->int:
        """
        Get or Set the gap width between two ticks.
        """
        GetDllLibPpt().ChartAxis_get_GapWidth.argtypes=[c_void_p]
        GetDllLibPpt().ChartAxis_get_GapWidth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartAxis_get_GapWidth,self.Ptr)
        return ret

    @GapWidth.setter
    def GapWidth(self, value:int):
        GetDllLibPpt().ChartAxis_set_GapWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartAxis_set_GapWidth,self.Ptr, value)

