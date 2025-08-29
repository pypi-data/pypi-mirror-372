from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDataTable (SpireObject) :
    """
    Represents data table format properties for a chart.
    """
    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill style properties of the chart data table.

        Returns:
            FillFormat: Read-only FillFormat object
        """
        GetDllLibPpt().ChartDataTable_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataTable_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets line style properties of the chart data table.

        Returns:
            IChartGridLine: Line style properties
        """
        GetDllLibPpt().ChartDataTable_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataTable_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets effects used for the chart data table.

        Returns:
            EffectDag: Read-only EffectDag object
        """
        GetDllLibPpt().ChartDataTable_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataTable_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Text(self)->'ITextFrameProperties':
        """
        Gets text properties used for the data table.

        Returns:
            ITextFrameProperties: Text properties object
        """
        GetDllLibPpt().ChartDataTable_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_Text.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataTable_get_Text,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets 3D format properties of the chart data table.

        Returns:
            FormatThreeD: Read-only 3D format properties
        """
        GetDllLibPpt().ChartDataTable_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataTable_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property
    def HasHorzBorder(self)->bool:
        """
        Indicates if the data table has horizontal borders.

        Returns:
            bool: True if horizontal borders are visible
        """
        GetDllLibPpt().ChartDataTable_get_HasHorzBorder.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_HasHorzBorder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataTable_get_HasHorzBorder,self.Ptr)
        return ret

    @HasHorzBorder.setter
    def HasHorzBorder(self, value:bool):
        GetDllLibPpt().ChartDataTable_set_HasHorzBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataTable_set_HasHorzBorder,self.Ptr, value)

    @property
    def HasBorders(self)->bool:
        """
        Indicates if the data table has any borders.

        Returns:
            bool: True if any borders are visible
        """
        GetDllLibPpt().ChartDataTable_get_HasBorders.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_HasBorders.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataTable_get_HasBorders,self.Ptr)
        return ret

    @HasBorders.setter
    def HasBorders(self, value:bool):
        GetDllLibPpt().ChartDataTable_set_HasBorders.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataTable_set_HasBorders,self.Ptr, value)

    @property
    def HasVertBorder(self)->bool:
        """
        Indicates if the data table has vertical borders.

        Returns:
            bool: True if vertical borders are visible
        """
        GetDllLibPpt().ChartDataTable_get_HasVertBorder.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_HasVertBorder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataTable_get_HasVertBorder,self.Ptr)
        return ret

    @HasVertBorder.setter
    def HasVertBorder(self, value:bool):
        GetDllLibPpt().ChartDataTable_set_HasVertBorder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataTable_set_HasVertBorder,self.Ptr, value)

    @property
    def ShowLegendKey(self)->bool:
        """
        Indicates that the data label has a legend key.

        Returns:
            bool: True if legend key is visible
        """
        GetDllLibPpt().ChartDataTable_get_ShowLegendKey.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataTable_get_ShowLegendKey.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataTable_get_ShowLegendKey,self.Ptr)
        return ret

    @ShowLegendKey.setter
    def ShowLegendKey(self, value:bool):
        GetDllLibPpt().ChartDataTable_set_ShowLegendKey.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataTable_set_ShowLegendKey,self.Ptr, value)

