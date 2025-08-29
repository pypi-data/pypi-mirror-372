from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ITrendlines (SpireObject) :
    """
    Specifies the type of trendline for a chart.
    """
    @property
    def backward(self)->float:
        """
        Gets or sets the number of periods that the trendline extends backward.

        Returns:
            float: The number of backward periods.
        """
        GetDllLibPpt().ITrendlines_get_backward.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_backward.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_backward,self.Ptr)
        return ret

    @backward.setter
    def backward(self, value:float):
        """
        Sets the number of periods that the trendline extends backward.

        Args:
            value (float): The number of backward periods to set.
        """
        GetDllLibPpt().ITrendlines_set_backward.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlines_set_backward,self.Ptr, value)

    @property
    def forward(self)->float:
        """
        Gets or sets the number of periods that the trendline extends forward.

        Returns:
            float: The number of forward periods.
        """
        GetDllLibPpt().ITrendlines_get_forward.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_forward.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_forward,self.Ptr)
        return ret

    @forward.setter
    def forward(self, value:float):
        """
        Sets the number of periods that the trendline extends forward.

        Args:
            value (float): The number of forward periods to set.
        """
        GetDllLibPpt().ITrendlines_set_forward.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlines_set_forward,self.Ptr, value)

    @property
    def intercept(self)->float:
        """
        Gets or sets the point where the trendline crosses the value axis.
        Supported only for exponential, linear, or polynomial trendlines.

        Returns:
            float: The intercept value.
        """
        GetDllLibPpt().ITrendlines_get_intercept.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_intercept.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_intercept,self.Ptr)
        return ret

    @intercept.setter
    def intercept(self, value:float):
        """
        Sets the point where the trendline crosses the value axis.

        Args:
            value (float): The intercept value to set.
        """
        GetDllLibPpt().ITrendlines_set_intercept.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlines_set_intercept,self.Ptr, value)

    @property
    def displayEquation(self)->bool:
        """
        Indicates whether the trendline equation is displayed on the chart.

        Returns:
            bool: True if equation is displayed, False otherwise.
        """
        GetDllLibPpt().ITrendlines_get_displayEquation.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_displayEquation.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_displayEquation,self.Ptr)
        return ret

    @displayEquation.setter
    def displayEquation(self, value:bool):
        """
        Sets whether to display the trendline equation on the chart.

        Args:
            value (bool): True to display equation, False to hide.
        """
        GetDllLibPpt().ITrendlines_set_displayEquation.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITrendlines_set_displayEquation,self.Ptr, value)

    @property
    def displayRSquaredValue(self)->bool:
        """
        Indicates whether the R-squared value is displayed on the chart.

        Returns:
            bool: True if R-squared value is displayed, False otherwise.
        """
        GetDllLibPpt().ITrendlines_get_displayRSquaredValue.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_displayRSquaredValue.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_displayRSquaredValue,self.Ptr)
        return ret

    @displayRSquaredValue.setter
    def displayRSquaredValue(self, value:bool):
        """
        Sets whether to display the R-squared value on the chart.

        Args:
            value (bool): True to display R-squared value, False to hide.
        """
        GetDllLibPpt().ITrendlines_set_displayRSquaredValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITrendlines_set_displayRSquaredValue,self.Ptr, value)

    @property
    def polynomialTrendlineOrder(self)->int:
        """
        Gets or sets the polynomial trendline order (between 2 and 6).

        Returns:
            int: The polynomial order value.
        """
        GetDllLibPpt().ITrendlines_get_polynomialTrendlineOrder.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_polynomialTrendlineOrder.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_polynomialTrendlineOrder,self.Ptr)
        return ret

    @polynomialTrendlineOrder.setter
    def polynomialTrendlineOrder(self, value:int):
        """
        Sets the polynomial trendline order.

        Args:
            value (int): The polynomial order between 2 and 6.
        """
        GetDllLibPpt().ITrendlines_set_polynomialTrendlineOrder.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITrendlines_set_polynomialTrendlineOrder,self.Ptr, value)

    @property
    def period(self)->int:
        """
        Gets or sets the moving average period (between 2 and 255).

        Returns:
            int: The period value.
        """
        GetDllLibPpt().ITrendlines_get_period.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_period.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_period,self.Ptr)
        return ret

    @period.setter
    def period(self, value:int):
        """
        Sets the moving average period.

        Args:
            value (int): The period between 2 and 255.
        """
        GetDllLibPpt().ITrendlines_set_period.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITrendlines_set_period,self.Ptr, value)

    @property

    def type(self)->'TrendlinesType':
        """
        Gets or sets the type of trendline.

        Returns:
            TrendlinesType: The trendline type enum value.
        """
        GetDllLibPpt().ITrendlines_get_type.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_type,self.Ptr)
        objwraped = TrendlinesType(ret)
        return objwraped

    @type.setter
    def type(self, value:'TrendlinesType'):
        """
        Sets the type of trendline.

        Args:
            value (TrendlinesType): The trendline type enum value.
        """
        GetDllLibPpt().ITrendlines_set_type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITrendlines_set_type,self.Ptr, value.value)

    @property

    def Name(self)->str:
        """
        Gets or sets the name of the trendline.

        Returns:
            str: The name of the trendline.
        """
        GetDllLibPpt().ITrendlines_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ITrendlines_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets the name of the trendline.

        Args:
            value (str): The name to set for the trendline.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ITrendlines_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ITrendlines_set_Name,self.Ptr,valuePtr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets the line formatting properties of the trendline.
        Read-only.

        Returns:
            TextLineFormat: The line formatting object.
        """
        GetDllLibPpt().ITrendlines_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITrendlines_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
        Gets the special effects applied to the trendline.
        Read-only.

        Returns:
            EffectDag: The special effects object.
        """
        GetDllLibPpt().ITrendlines_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITrendlines_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def TrendLineLabel(self)->'ITrendlineLabel':
        """
        Gets the data label associated with the trendline.
        Read-only.

        Returns:
            ITrendlineLabel: The trendline label object.
        """
        GetDllLibPpt().ITrendlines_get_TrendLineLabel.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_TrendLineLabel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITrendlines_get_TrendLineLabel,self.Ptr)
        ret = None if intPtr==None else ITrendlineLabel(intPtr)
        return ret


