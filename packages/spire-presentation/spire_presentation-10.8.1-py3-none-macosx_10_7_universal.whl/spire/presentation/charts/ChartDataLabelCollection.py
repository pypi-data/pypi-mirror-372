from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDataLabelCollection (  SpireObject ) :
    """
    Represents a collection of data labels for a chart series.
    Provides properties and methods to manage the appearance, formatting, and behavior of data labels in a chart.
    """
    @property

    def NumberFormat(self)->str:
        """
        Gets or sets the number formatting string for data label values.
        
        Returns:
            str: The current number format string
        """
        GetDllLibPpt().ChartDataLabelCollection_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_NumberFormat,self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartDataLabelCollection_set_NumberFormat.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_NumberFormat,self.Ptr,valuePtr)

    @property
    def HasDataSource(self)->bool:
        """
        Gets and sets a reference to the worksheet
        
        Returns:
            bool: whethere use worksheet data. 
        """
        GetDllLibPpt().ChartDataLabelCollection_get_HasDataSource.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_HasDataSource.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_HasDataSource,self.Ptr)
        return ret

    @HasDataSource.setter
    def HasDataSource(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_HasDataSource.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_HasDataSource,self.Ptr, value)

    @property
    def IsDelete(self)->bool:
        """
        Gets or sets delete flag.
        
        Returns:
            bool: whethere delete the data label. 
        """
        GetDllLibPpt().ChartDataLabelCollection_get_IsDelete.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_IsDelete.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_IsDelete,self.Ptr)
        return ret

    @IsDelete.setter
    def IsDelete(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_IsDelete.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_IsDelete,self.Ptr, value)

    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
        Gets a text properties of this data labels.
        
        Returns:
            ITextFrameProperties: text properties of this data labels.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill style properties of a data label.
        
        Returns:
            FillFormat: fill style properties of a data label.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets line style properties of data labels.
        
        Returns:
            IChartGridLine: line style properties of data labels.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets effects used for data labels.
        
        Returns:
            EffectDag: effects style of data labels.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets 3D format of data labels.
        
        Returns:
            FormatThreeD: 3D format of data labels.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def Position(self)->'ChartDataLabelPosition':
        """
        Represents the position of the data lable.
        
        Returns:
            ChartDataLabelPosition: the position of the data lable.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Position,self.Ptr)
        objwraped = ChartDataLabelPosition(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'ChartDataLabelPosition'):
        GetDllLibPpt().ChartDataLabelCollection_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_Position,self.Ptr, value.value)

    @property
    def LegendKeyVisible(self)->bool:
        """
        Indicates chart's data label legend key display behavior. 
        
        Returns:
            bool: whethere chart's data label legend key display.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_LegendKeyVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_LegendKeyVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_LegendKeyVisible,self.Ptr)
        return ret

    @LegendKeyVisible.setter
    def LegendKeyVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_LegendKeyVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_LegendKeyVisible,self.Ptr, value)

    @property
    def LeaderLinesVisible(self)->bool:
        """
        Indicates chart's data label leader line display behavior. 
        
        Returns:
            bool: whethere chart's data label leader line display.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_LeaderLinesVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_LeaderLinesVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_LeaderLinesVisible,self.Ptr)
        return ret

    @LeaderLinesVisible.setter
    def LeaderLinesVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_LeaderLinesVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_LeaderLinesVisible,self.Ptr, value)

    @property
    def CategoryNameVisible(self)->bool:
        """
        Indicates chart's data label category name display behavior.
        
        Returns:
            bool: whethere chart's data label category name display.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_CategoryNameVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_CategoryNameVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_CategoryNameVisible,self.Ptr)
        return ret

    @CategoryNameVisible.setter
    def CategoryNameVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_CategoryNameVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_CategoryNameVisible,self.Ptr, value)

    @property
    def LabelValueVisible(self)->bool:
        """
        Indicates chart's data label value display behavior.
        
        Returns:
            bool: whethere chart's data label value display.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_LabelValueVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_LabelValueVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_LabelValueVisible,self.Ptr)
        return ret

    @LabelValueVisible.setter
    def LabelValueVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_LabelValueVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_LabelValueVisible,self.Ptr, value)

    @property
    def PercentValueVisible(self)->bool:
        """
        Indicates chart's data label percentage value display behavior.
        
        Returns:
            bool: whethere chart's data label percentage value display.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_PercentValueVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_PercentValueVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_PercentValueVisible,self.Ptr)
        return ret

    @PercentValueVisible.setter
    def PercentValueVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_PercentValueVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_PercentValueVisible,self.Ptr, value)

    @property
    def SeriesNameVisible(self)->bool:
        """
        Gets or sets a Boolean to indicate the series name display behavior for the data labels on a chart.
        
        Returns:
            bool: whethere the series name display.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_SeriesNameVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_SeriesNameVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_SeriesNameVisible,self.Ptr)
        return ret

    @SeriesNameVisible.setter
    def SeriesNameVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_SeriesNameVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_SeriesNameVisible,self.Ptr, value)

    @property
    def BubbleSizeVisible(self)->bool:
        """
        Indicates chart's data label bubble size value display behavior.
        
        Returns:
            bool: whethere data label bubble size value display.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_BubbleSizeVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_BubbleSizeVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_BubbleSizeVisible,self.Ptr)
        return ret

    @BubbleSizeVisible.setter
    def BubbleSizeVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_BubbleSizeVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_BubbleSizeVisible,self.Ptr, value)

    @property

    def Separator(self)->str:
        """
        Sets or returns a Variant representing the separator used for the data labels on a chart.
        
        Returns:
            str: the separator used for the data labels on a chart.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Separator.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Separator.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Separator,self.Ptr))
        return ret


    @Separator.setter
    def Separator(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartDataLabelCollection_set_Separator.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_Separator,self.Ptr,valuePtr)

    @property
    def Count(self)->int:
        """
        Gets the number of elements actually contained in the collection.
        
        Returns:
            int: the number of elements actually contained in the collection.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Count,self.Ptr)
        return ret

    @property

    def DataLabelShapeType(self)->'DataLabelShapeType':
        """
        Gets or sets shape type of data labels.
        
        Returns:
            DataLabelShapeType: DataLabel shape type.
        """
        GetDllLibPpt().ChartDataLabelCollection_get_DataLabelShapeType.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_DataLabelShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_DataLabelShapeType,self.Ptr)
        objwraped = DataLabelShapeType(ret)
        return objwraped

    @DataLabelShapeType.setter
    def DataLabelShapeType(self, value:'DataLabelShapeType'):
        GetDllLibPpt().ChartDataLabelCollection_set_DataLabelShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_DataLabelShapeType,self.Ptr, value.value)


    def Add(self)->'ChartDataLabel':
        """
        Add ChartDataLabel.
        
        Returns:
            ChartDataLabel: chart datalabel.
        """
        GetDllLibPpt().ChartDataLabelCollection_Add.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_Add,self.Ptr)
        ret = None if intPtr==None else ChartDataLabel(intPtr)
        return ret



    def Remove(self ,value:'ChartDataLabel'):
        """
        Add ChartDataLabel.
        
        Args:
            value: chart datalabel which will be removed..
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartDataLabelCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_Remove,self.Ptr, intPtrvalue)


    def IndexOf(self ,value:'ChartDataLabel')->int:
        """
        Gets the index of a specific data label.
        
        Args:
            value (ChartDataLabel): The data label to locate
            
        Returns:
            int: The zero-based index if found; otherwise, -1
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartDataLabelCollection_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_IndexOf,self.Ptr, intPtrvalue)
        return ret

    @dispatch
    def __getitem__(self, index):
        """
        Gets the data label at the specified index.
        
        Args:
            index: The zero-based index of the label to retrieve
            
        Returns:
            ChartDataLabel: The data label at the specified position
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().ChartDataLabelCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartDataLabelCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartDataLabel(intPtr)
        return ret

    def get_Item(self ,index:int)->'ChartDataLabel':
        """
        Gets the data label at the specified index.
        
        Args:
            index: The zero-based index of the label to retrieve
            
        Returns:
            ChartDataLabel: The data label at the specified position
        """
        
        GetDllLibPpt().ChartDataLabelCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartDataLabelCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartDataLabel(intPtr)
        return ret


    @property

    def LeaderLines(self)->'IChartGridLine':
        """
        Gets the formatting for leader lines connecting labels to data points.
        
        Returns:
            IChartGridLine: The leader lines formatting object
        """
        GetDllLibPpt().ChartDataLabelCollection_get_LeaderLines.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_LeaderLines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_LeaderLines,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator to iterate through the data label collection.
        
        Returns:
            IEnumerator: An enumerator for the collection
        """
        GetDllLibPpt().ChartDataLabelCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


