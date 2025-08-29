from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartTextArea (SpireObject) :
    """
    Represents text area properties for chart elements.
    """
    @property
    def Left(self)->float:
        """
        Gets or sets the x-coordinate in points.
        """
        GetDllLibPpt().ChartTextArea_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartTextArea_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().ChartTextArea_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartTextArea_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets the y-coordinate in points.
        """
        GetDllLibPpt().ChartTextArea_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartTextArea_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().ChartTextArea_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartTextArea_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets the width in points.
        """
        GetDllLibPpt().ChartTextArea_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartTextArea_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().ChartTextArea_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartTextArea_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets the height of a legend in points.
    
        """
        GetDllLibPpt().ChartTextArea_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartTextArea_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().ChartTextArea_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartTextArea_set_Height,self.Ptr, value)

    @property
    def IsOverlay(self)->bool:
        """
        Indicates whether allowed to overlap title.
           
        """
        GetDllLibPpt().ChartTextArea_get_IsOverlay.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_IsOverlay.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartTextArea_get_IsOverlay,self.Ptr)
        return ret

    @IsOverlay.setter
    def IsOverlay(self, value:bool):
        GetDllLibPpt().ChartTextArea_set_IsOverlay.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartTextArea_set_IsOverlay,self.Ptr, value)

    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
        Gets text frame of a chart title.
  
        """
        GetDllLibPpt().ChartTextArea_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartTextArea_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets the fill style properties.
        Read-only FillFormat.
        """
        GetDllLibPpt().ChartTextArea_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartTextArea_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets the line style properties.
        """
        GetDllLibPpt().ChartTextArea_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartTextArea_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets the effects applied to the text area.
        Read-only EffectDag.
        """
        GetDllLibPpt().ChartTextArea_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartTextArea_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets the 3D formatting properties.
        Read-only FormatThreeD.
        """
        GetDllLibPpt().ChartTextArea_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartTextArea_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartTextArea_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


