from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDataLabel (  PptObject) :
    """
    Represents a series label for a chart data point.
    """
    @property

    def DataLabelSize(self)->'SizeF':
        """
        Gets or sets the size of the data label.

        Returns:
            SizeF: Current size of the data label
        """
        GetDllLibPpt().ChartDataLabel_get_DataLabelSize.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_DataLabelSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_DataLabelSize,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @DataLabelSize.setter
    def DataLabelSize(self, value:'SizeF'):
        GetDllLibPpt().ChartDataLabel_set_DataLabelSize.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_DataLabelSize,self.Ptr, value.Ptr)

    @property
    def IsDelete(self)->bool:
        """
        Indicates if the label was deleted by user but preserved in file.

        Returns:
            bool: True if marked for deletion
        """
        GetDllLibPpt().ChartDataLabel_get_IsDelete.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_IsDelete.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_IsDelete,self.Ptr)
        return ret

    @IsDelete.setter
    def IsDelete(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_IsDelete.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_IsDelete,self.Ptr, value)

    @property
    def ID(self)->int:
        """
        Specifies which data labels the properties apply to.

        Returns:
            int: Identifier for the data label
        """
        GetDllLibPpt().ChartDataLabel_get_ID.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_ID.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_ID,self.Ptr)
        return ret

    @ID.setter
    def ID(self, value:int):
        GetDllLibPpt().ChartDataLabel_set_ID.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_ID,self.Ptr, value)

    @property
    def HasDataSource(self)->bool:
        """
        Indicates if the data label has a reference to a worksheet.

        Returns:
            bool: True if has data source reference
        """
        GetDllLibPpt().ChartDataLabel_get_HasDataSource.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_HasDataSource.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_HasDataSource,self.Ptr)
        return ret

    @HasDataSource.setter
    def HasDataSource(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_HasDataSource.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_HasDataSource,self.Ptr, value)

    @property

    def NumberFormat(self)->str:
        """
        Gets or sets the format string for the data label.

        Returns:
            str: Number format string
        """
        GetDllLibPpt().ChartDataLabel_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabel_get_NumberFormat,self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartDataLabel_set_NumberFormat.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_NumberFormat,self.Ptr,valuePtr)

    @property

    def TextFrame(self)->'ITextFrameProperties':
        """
        Gets text frame properties of the data label.

        Returns:
            ITextFrameProperties: Text frame properties
        """
        GetDllLibPpt().ChartDataLabel_get_TextFrame.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_TextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
        Gets text properties of the data label.

        Returns:
            ITextFrameProperties: Read-only text properties
        """
        GetDllLibPpt().ChartDataLabel_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill style properties of the data label.

        Returns:
            FillFormat: Read-only FillFormat object
        """
        GetDllLibPpt().ChartDataLabel_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets line style properties of the data label.

        Returns:
            IChartGridLine: Line style properties
        """
        GetDllLibPpt().ChartDataLabel_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets effects used for the data label.

        Returns:
            EffectDag: Read-only EffectDag object
        """
        GetDllLibPpt().ChartDataLabel_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets 3D format properties of the data label.

        Returns:
            FormatThreeD: Read-only 3D format properties
        """
        GetDllLibPpt().ChartDataLabel_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def Position(self)->'ChartDataLabelPosition':
        """
        Gets or sets the position of the data label.

        Returns:
            ChartDataLabelPosition: Current position value
        """
        GetDllLibPpt().ChartDataLabel_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Position,self.Ptr)
        objwraped = ChartDataLabelPosition(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'ChartDataLabelPosition'):
        GetDllLibPpt().ChartDataLabel_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_Position,self.Ptr, value.value)

    @property
    def LegendKeyVisible(self)->bool:
        """
        Indicates whethere chart's data label legend key display behavior. 

        Returns:
            bool:whethere chart's data label legend key display.
        """
        GetDllLibPpt().ChartDataLabel_get_LegendKeyVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_LegendKeyVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_LegendKeyVisible,self.Ptr)
        return ret

    @LegendKeyVisible.setter
    def LegendKeyVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_LegendKeyVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_LegendKeyVisible,self.Ptr, value)

    @property
    def CategoryNameVisible(self)->bool:
        """
        Indicates whethere chart's data label category name display behavior.

        Returns:
            bool:whethere chart's data label category name display.
        """
        GetDllLibPpt().ChartDataLabel_get_CategoryNameVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_CategoryNameVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_CategoryNameVisible,self.Ptr)
        return ret

    @CategoryNameVisible.setter
    def CategoryNameVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_CategoryNameVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_CategoryNameVisible,self.Ptr, value)

    @property
    def LabelValueVisible(self)->bool:
        """
        Indicates whethere chart's data label percentage value display behavior. 

        Returns:
            bool:whethere chart's data label percentage value display.
        """
        GetDllLibPpt().ChartDataLabel_get_LabelValueVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_LabelValueVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_LabelValueVisible,self.Ptr)
        return ret

    @LabelValueVisible.setter
    def LabelValueVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_LabelValueVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_LabelValueVisible,self.Ptr, value)

    @property
    def PercentageVisible(self)->bool:
        """
        Indicates whethere chart's data label percentage value display behavior.

        Returns:
            bool:whethere chart's data label percentage value display.
        """
        GetDllLibPpt().ChartDataLabel_get_PercentageVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_PercentageVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_PercentageVisible,self.Ptr)
        return ret

    @PercentageVisible.setter
    def PercentageVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_PercentageVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_PercentageVisible,self.Ptr, value)

    @property
    def SeriesNameVisible(self)->bool:
        """
        Indicates whethere the series name display behavior for the data labels on a chart. 

        Returns:
            bool:whethere the series name display.
        """
        GetDllLibPpt().ChartDataLabel_get_SeriesNameVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_SeriesNameVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_SeriesNameVisible,self.Ptr)
        return ret

    @SeriesNameVisible.setter
    def SeriesNameVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_SeriesNameVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_SeriesNameVisible,self.Ptr, value)

    @property
    def BubbleSizeVisible(self)->bool:
        """
        Indicates whethere chart's data label bubble size value will display. 

        Returns:
            bool:whethere chart's data label bubble size value will display.
        """
        
        GetDllLibPpt().ChartDataLabel_get_BubbleSizeVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_BubbleSizeVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_BubbleSizeVisible,self.Ptr)
        return ret

    @BubbleSizeVisible.setter
    def BubbleSizeVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_BubbleSizeVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_BubbleSizeVisible,self.Ptr, value)

    @property

    def Separator(self)->str:
        """
        Gets or sets the separator used for the data labels on a chart.

        Returns:
            str:the separator used for the data labels.
        """
        GetDllLibPpt().ChartDataLabel_get_Separator.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Separator.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabel_get_Separator,self.Ptr))
        return ret


    @Separator.setter
    def Separator(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartDataLabel_set_Separator.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_Separator,self.Ptr,valuePtr)

    @property
    def X(self)->float:
        """
        Specifies the x location(left) of the dataLabel as a fraction of the width of the chart.
        The position is relative to the default position.

        Returns:
            float:the x location(left) of the dataLabel.
        """
        GetDllLibPpt().ChartDataLabel_get_X.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_X.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_X,self.Ptr)
        return ret

    @X.setter
    def X(self, value:float):
        GetDllLibPpt().ChartDataLabel_set_X.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_X,self.Ptr, value)

    @property
    def Y(self)->float:
        """
        Specifies the y location(top) of the dataLabel as a fraction of the height of the chart.
        The position is relative to the default position.

        Returns:
            float:the y location(top) of the dataLabel.
        """
        GetDllLibPpt().ChartDataLabel_get_Y.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Y.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Y,self.Ptr)
        return ret

    @Y.setter
    def Y(self, value:float):
        GetDllLibPpt().ChartDataLabel_set_Y.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_Y,self.Ptr, value)

    @property
    def RotationAngle(self)->float:
        """
        Gets or sets rotation angle of chart's data label.

        Returns:
            float:rotation angle of chart's data label.
        """
        GetDllLibPpt().ChartDataLabel_get_RotationAngle.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_RotationAngle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_RotationAngle,self.Ptr)
        return ret

    @RotationAngle.setter
    def RotationAngle(self, value:float):
        GetDllLibPpt().ChartDataLabel_set_RotationAngle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_RotationAngle,self.Ptr, value)

    @property

    def DataLabelShapeType(self)->'DataLabelShapeType':
        """
        Gets or sets shape type of data label.

        Returns:
            DataLabelShapeType:shape type of data label..
        """
        GetDllLibPpt().ChartDataLabel_get_DataLabelShapeType.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_DataLabelShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_DataLabelShapeType,self.Ptr)
        objwraped = DataLabelShapeType(ret)
        return objwraped

    @DataLabelShapeType.setter
    def DataLabelShapeType(self, value:'DataLabelShapeType'):
        GetDllLibPpt().ChartDataLabel_set_DataLabelShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_DataLabelShapeType,self.Ptr, value.value)

    @property
    def ShowDataLabelsRange(self)->bool:
        """
        if show data labels range.

        Returns:
            bool:whethere show data labels range.
        """
        GetDllLibPpt().ChartDataLabel_get_ShowDataLabelsRange.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_ShowDataLabelsRange.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_ShowDataLabelsRange,self.Ptr)
        return ret

    @ShowDataLabelsRange.setter
    def ShowDataLabelsRange(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_ShowDataLabelsRange.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_ShowDataLabelsRange,self.Ptr, value)

    @property
    def UseValuePlaceholder(self)->bool:
        """
        If use ValuePlaceholder.

        Returns:
            bool:whethere use ValuePlaceholder.
        """
        GetDllLibPpt().ChartDataLabel_get_UseValuePlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_UseValuePlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_UseValuePlaceholder,self.Ptr)
        return ret

    @UseValuePlaceholder.setter
    def UseValuePlaceholder(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_UseValuePlaceholder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_UseValuePlaceholder,self.Ptr, value)

    @staticmethod

    def ValuePlaceholder()->str:
        """
        Use the ValuePlaceholder to represent chart value

        Returns:
            str:value placeholder.
        """
        #GetDllLibPpt().ChartDataLabel_ValuePlaceholder.argtypes=[]
        GetDllLibPpt().ChartDataLabel_ValuePlaceholder.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabel_ValuePlaceholder))
        return ret


