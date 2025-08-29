from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ChartDataPoint (  PptObject) :
    """
    Represents an individual data point within a chart series.
    
    This class provides properties to control the visual appearance and behavior
    of individual data points in a chart.
    """

    @dispatch
    def __init__(self):
        """Initializes a new instance of ChartDataPoint."""
        GetDllLibPpt().ChartDataPoint_Creat.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_Creat)
        super(ChartDataPoint, self).__init__(intPtr)

    @dispatch
    def __init__(self,param):
        """
        Initializes a new instance of ChartDataPoint.
        
        Args:
            param: Either a numeric value or another ChartDataPoint to clone
        """
        if isinstance(param, (int,float)):
            super(ChartDataPoint, self).__init__(param)
        else:
            GetDllLibPpt().ChartDataPoint_Creat.argtypes = [c_void_p]
            GetDllLibPpt().ChartDataPoint_Creat.restype = c_void_p
            intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_Creat,param.Ptr)
            super(ChartDataPoint, self).__init__(intPtr)
  
    @property
    def Index(self)->int:
        """
        Indicates whether bubbles have a 3D effect applied.
        
        Returns:
            bool: True if 3D effect is enabled for bubbles
        """
        GetDllLibPpt().ChartDataPoint_get_Index.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Index,self.Ptr)
        return ret

    @Index.setter
    def Index(self, value:int):
        GetDllLibPpt().ChartDataPoint_set_Index.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_Index,self.Ptr, value)

    @property
    def IsBubble3D(self)->bool:
        """
        Indicates whether bubbles have a 3D effect applied.
        
        Returns:
            bool: True if 3D effect is enabled for bubbles
        """
        GetDllLibPpt().ChartDataPoint_get_IsBubble3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_IsBubble3D.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_IsBubble3D,self.Ptr)
        return ret

    @IsBubble3D.setter
    def IsBubble3D(self, value:bool):
        GetDllLibPpt().ChartDataPoint_set_IsBubble3D.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_IsBubble3D,self.Ptr, value)

    @property
    def Distance(self)->int:
        """
        Specifies the distance from the center of a pie chart (for slice explosion).
        
        Returns:
            int: Distance value (0-100)
        """
        GetDllLibPpt().ChartDataPoint_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Distance.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Distance,self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:int):
        GetDllLibPpt().ChartDataPoint_set_Distance.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_Distance,self.Ptr, value)

    @property
    def InvertIfNegative(self)->bool:
        """
        Indicates whether colors should be inverted for negative values.
        
        Returns:
            bool: True if colors should invert for negative values
        """
        GetDllLibPpt().ChartDataPoint_get_InvertIfNegative.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_InvertIfNegative.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_InvertIfNegative,self.Ptr)
        return ret

    @InvertIfNegative.setter
    def InvertIfNegative(self, value:bool):
        GetDllLibPpt().ChartDataPoint_set_InvertIfNegative.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_InvertIfNegative,self.Ptr, value)

    @property

    def Fill(self)->'FillFormat':
        """
        Gets the fill formatting properties for the data point.
        
        Returns:
            FillFormat: Object containing fill properties
        """
        GetDllLibPpt().ChartDataPoint_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets the line formatting properties for the data point.
        
        Returns:
            IChartGridLine: Object containing line properties
        """
        GetDllLibPpt().ChartDataPoint_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets the effect properties for the data point.
        
        Returns:
            EffectDag: Object containing effect properties
        """
        GetDllLibPpt().ChartDataPoint_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets the 3D format properties for the data point.
        
        Returns:
            FormatThreeD: Object containing 3D format properties
        """
        GetDllLibPpt().ChartDataPoint_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def MarkerFill(self)->'ChartEffectFormat':
        """
        Gets the formatting properties for data point markers.
        
        Returns:
            ChartEffectFormat: Object containing marker properties
        """
        GetDllLibPpt().ChartDataPoint_get_MarkerFill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_MarkerFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_MarkerFill,self.Ptr)
        ret = None if intPtr==None else ChartEffectFormat(intPtr)
        return ret


    @property
    def MarkerSize(self)->int:
        """
        Gets or sets the size of markers in line/scatter/radar charts.
        
        Returns:
            int: Marker size in points
        """
        GetDllLibPpt().ChartDataPoint_get_MarkerSize.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_MarkerSize.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_MarkerSize,self.Ptr)
        return ret

    @MarkerSize.setter
    def MarkerSize(self, value:int):
        GetDllLibPpt().ChartDataPoint_set_MarkerSize.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_MarkerSize,self.Ptr, value)

    @property

    def MarkerStyle(self)->'ChartMarkerType':
        """
        Gets or sets the style of markers in line/scatter/radar charts.
        
        Returns:
            ChartMarkerType: Enum value specifying marker style
        """
        GetDllLibPpt().ChartDataPoint_get_MarkerStyle.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_MarkerStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_MarkerStyle,self.Ptr)
        objwraped = ChartMarkerType(ret)
        return objwraped

    @MarkerStyle.setter
    def MarkerStyle(self, value:'ChartMarkerType'):
        GetDllLibPpt().ChartDataPoint_set_MarkerStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_MarkerStyle,self.Ptr, value.value)

    @property
    def SetAsTotal(self)->bool:
        """
        Indicates if the data point represents a total in waterfall charts.
        
        Returns:
            bool: True if data point is a total
        """
        GetDllLibPpt().ChartDataPoint_get_SetAsTotal.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_SetAsTotal.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_SetAsTotal,self.Ptr)
        return ret

    @SetAsTotal.setter
    def SetAsTotal(self, value:bool):
        GetDllLibPpt().ChartDataPoint_set_SetAsTotal.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_SetAsTotal,self.Ptr, value)

