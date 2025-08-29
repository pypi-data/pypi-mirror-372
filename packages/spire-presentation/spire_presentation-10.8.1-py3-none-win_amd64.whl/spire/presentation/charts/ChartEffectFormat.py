from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartEffectFormat (  PptObject, IChartEffectFormat) :
    """
    Represents chart format properties.
    """
    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill style properties of a chart.

        Returns:
            FillFormat: Read-only FillFormat object
        """
        GetDllLibPpt().ChartEffectFormat_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartEffectFormat_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartEffectFormat_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets line style properties of a chart.

        Returns:
            IChartGridLine: Line style properties
        """
        GetDllLibPpt().ChartEffectFormat_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartEffectFormat_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartEffectFormat_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets effects used for a chart.

        Returns:
            EffectDag: Read-only EffectDag object
        """
        GetDllLibPpt().ChartEffectFormat_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartEffectFormat_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartEffectFormat_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets 3D format of a chart.

        Returns:
            FormatThreeD: Read-only 3D format properties
        """
        GetDllLibPpt().ChartEffectFormat_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartEffectFormat_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartEffectFormat_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


