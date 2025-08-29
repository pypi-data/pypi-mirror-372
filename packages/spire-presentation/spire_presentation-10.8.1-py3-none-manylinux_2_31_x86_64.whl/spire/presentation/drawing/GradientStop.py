from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStop (SpireObject) :
    """
    Represents a gradient stop point in a gradient fill.
    """
    @property
    def Position(self)->float:
        """
        Gets or sets the position (0..1) of a gradient stop.
        """
        GetDllLibPpt().GradientStop_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().GradientStop_get_Position.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GradientStop_get_Position,self.Ptr)
        return ret

    @Position.setter
    def Position(self, value:float):
        GetDllLibPpt().GradientStop_set_Position.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().GradientStop_set_Position,self.Ptr, value)

    @property

    def Color(self)->'ColorFormat':
        """
        Gets the color of a gradient stop.
        """
        GetDllLibPpt().GradientStop_get_Color.argtypes=[c_void_p]
        GetDllLibPpt().GradientStop_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStop_get_Color,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


