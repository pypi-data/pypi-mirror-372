from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStopData (SpireObject) :
    """
    Represents a gradient stop.
    
    """
    @property
    def Position(self)->float:
        """
        Gets the position (0..1) of a gradient stop.
        """
        GetDllLibPpt().GradientStopData_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopData_get_Position.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GradientStopData_get_Position,self.Ptr)
        return ret

    @property

    def Color(self)->'Color':
        """
        Gets the color of a gradient stop.
        """
        GetDllLibPpt().GradientStopData_get_Color.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopData_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopData_get_Color,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


