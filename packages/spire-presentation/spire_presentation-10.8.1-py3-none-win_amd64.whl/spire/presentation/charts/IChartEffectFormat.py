from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IChartEffectFormat (SpireObject) :
    """
    Represents visual effect formatting for chart elements.

    This class provides access to fill, line, 3D, and special effect 
    properties for chart components like series and markers.
    """
    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill style properties (read-only).
        """
        GetDllLibPpt().IChartEffectFormat_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets line style properties (read-only).
        """
        GetDllLibPpt().IChartEffectFormat_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets special effects (read-only).
        """
        GetDllLibPpt().IChartEffectFormat_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets 3D format properties (read-only).
        """
        GetDllLibPpt().IChartEffectFormat_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
        Reference to parent object (read-only).
        """
        GetDllLibPpt().IChartEffectFormat_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def Dispose(self):
        """
        Releases resources associated with the effect format.
        """
        GetDllLibPpt().IChartEffectFormat_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IChartEffectFormat_Dispose,self.Ptr)

