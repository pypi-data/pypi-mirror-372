from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartWallsOrFloor (  PptObject) :
    """
    Represents walls or floor on 3D charts.
    """
    @property
    def Thickness(self)->int:
        """
        Gets or sets the thickness of the walls or floor.

        Returns:
            int: The thickness value.
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Thickness.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Thickness.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Thickness,self.Ptr)
        return ret

    @Thickness.setter
    def Thickness(self, value:int):
        GetDllLibPpt().ChartWallsOrFloor_set_Thickness.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartWallsOrFloor_set_Thickness,self.Ptr, value)

    @property

    def Fill(self)->'FillFormat':
        """
        Gets the fill style properties of the chart walls or floor.

        Returns:
            FillFormat: Read-only fill format object.
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
        Gets the line style properties of the chart walls or floor.

        Returns:
            IChartGridLine: Line style object.
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets effects used for the chart walls or floor.

        Returns:
            EffectDag: Read-only effect object.
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
        Gets 3D format of the chart walls or floor.

        Returns:
            FormatThreeD: Read-only 3D format object.
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def PictureType(self)->'PictureType':
        """
        Gets or sets the picture type for the walls or floor.

        Returns:
            PictureType: Enum value representing picture type.
        """
        GetDllLibPpt().ChartWallsOrFloor_get_PictureType.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_PictureType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_PictureType,self.Ptr)
        objwraped = PictureType(ret)
        return objwraped

    @PictureType.setter
    def PictureType(self, value:'PictureType'):
        GetDllLibPpt().ChartWallsOrFloor_set_PictureType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartWallsOrFloor_set_PictureType,self.Ptr, value.value)

