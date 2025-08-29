from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LayoutProperty (SpireObject) :
    """
    Contains advanced layout properties for specialized chart types.

    Provides configuration options for waterfall and box-whisker charts.
    """
    @property
    def ShowConnectorLines(self)->bool:
        """
        Indicates whether connector lines are displayed (Waterfall charts).

        Returns:
            bool: True to show connector lines, False to hide.
        """
        GetDllLibPpt().LayoutProperty_get_ShowConnectorLines.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowConnectorLines.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowConnectorLines,self.Ptr)
        return ret

    @ShowConnectorLines.setter
    def ShowConnectorLines(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowConnectorLines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowConnectorLines,self.Ptr, value)

    @property
    def ShowMeanLine(self)->bool:
        """
        Indicates whether mean line is displayed (Box-Whisker charts).

        Returns:
            bool: True to show mean line, False to hide.
        """
        GetDllLibPpt().LayoutProperty_get_ShowMeanLine.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowMeanLine.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowMeanLine,self.Ptr)
        return ret

    @ShowMeanLine.setter
    def ShowMeanLine(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowMeanLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowMeanLine,self.Ptr, value)

    @property
    def ShowMeanMarkers(self)->bool:
        """
        Indicates whether mean markers are displayed (Box-Whisker charts).

        Returns:
            bool: True to show markers, False to hide.
        """
        GetDllLibPpt().LayoutProperty_get_ShowMeanMarkers.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowMeanMarkers.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowMeanMarkers,self.Ptr)
        return ret

    @ShowMeanMarkers.setter
    def ShowMeanMarkers(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowMeanMarkers.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowMeanMarkers,self.Ptr, value)

    @property
    def ShowOutlierPoints(self)->bool:
        """
        Indicates whether outlier points are shown (Box-Whisker charts).

        Returns:
            bool: True to show outliers, False to hide.
        """
        GetDllLibPpt().LayoutProperty_get_ShowOutlierPoints.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowOutlierPoints.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowOutlierPoints,self.Ptr)
        return ret

    @ShowOutlierPoints.setter
    def ShowOutlierPoints(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowOutlierPoints.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowOutlierPoints,self.Ptr, value)

    @property
    def ShowInnerPoints(self)->bool:
        """
        Indicates whether inner points are shown (Box-Whisker charts).

        Returns:
            bool: True to show inner points, False to hide.
        """
        GetDllLibPpt().LayoutProperty_get_ShowInnerPoints.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowInnerPoints.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowInnerPoints,self.Ptr)
        return ret

    @ShowInnerPoints.setter
    def ShowInnerPoints(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowInnerPoints.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowInnerPoints,self.Ptr, value)

    @property

    def QuartileCalculationType(self)->'QuartileCalculation':
        """
        Gets/sets quartile calculation method (Box-Whisker charts).

        Returns:
            QuartileCalculation: Current calculation method.
        """
        GetDllLibPpt().LayoutProperty_get_QuartileCalculationType.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_QuartileCalculationType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_QuartileCalculationType,self.Ptr)
        objwraped = QuartileCalculation(ret)
        return objwraped

    @QuartileCalculationType.setter
    def QuartileCalculationType(self, value:'QuartileCalculation'):
        GetDllLibPpt().LayoutProperty_set_QuartileCalculationType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_QuartileCalculationType,self.Ptr, value.value)

