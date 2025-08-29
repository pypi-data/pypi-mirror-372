from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartPlotArea (SpireObject) :
    """
    Represents the area where a chart is plotted.
    
    This class controls the visual appearance and dimensions of the plot area.
    """
    @property

    def Fill(self)->'FillFormat':
        """
        Gets the fill formatting properties for the plot area.
        
        Returns:
            FillFormat: Object containing fill properties
        """
        GetDllLibPpt().ChartPlotArea_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets the line formatting properties for the plot area border.
        
        Returns:
            IChartGridLine: Object containing line properties
        """
        GetDllLibPpt().ChartPlotArea_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets the effect properties for the plot area.
        
        Returns:
            EffectDag: Object containing effect properties
        """
        GetDllLibPpt().ChartPlotArea_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets the 3D format properties for the plot area.
        
        Returns:
            FormatThreeD: Object containing 3D properties
        """
        GetDllLibPpt().ChartPlotArea_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property
    def Left(self)->float:
        """
        Gets or sets the position from left (0-1 as fraction of chart area).
        
        Returns:
            float: Position from left (0.0 to 1.0)
        """
        GetDllLibPpt().ChartPlotArea_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().ChartPlotArea_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartPlotArea_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets the position from top (0-1 as fraction of chart area).
        
        Returns:
            float: Position from top (0.0 to 1.0)
        """
        GetDllLibPpt().ChartPlotArea_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().ChartPlotArea_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartPlotArea_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets the width of the plot area (0-1 as fraction of chart area).
        
        Returns:
            float: Width (0.0 to 1.0)
        """
        GetDllLibPpt().ChartPlotArea_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().ChartPlotArea_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartPlotArea_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets the height of the plot area (0-1 as fraction of chart area).
        
        Returns:
            float: Height (0.0 to 1.0)
        """
        GetDllLibPpt().ChartPlotArea_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().ChartPlotArea_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartPlotArea_set_Height,self.Ptr, value)

