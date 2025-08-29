from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IErrorBarsFormat (SpireObject) :
    """
    anages error bar formatting for chart series.

    Controls error bar type, values, and visual representation.
    """
    @property

    def ErrorBarvType(self)->'ErrorValueType':
        """
        Gets or sets the ErrorBarValueType.
    
        """
        GetDllLibPpt().IErrorBarsFormat_get_ErrorBarvType.argtypes=[c_void_p]
        GetDllLibPpt().IErrorBarsFormat_get_ErrorBarvType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IErrorBarsFormat_get_ErrorBarvType,self.Ptr)
        objwraped = ErrorValueType(ret)
        return objwraped

    @ErrorBarvType.setter
    def ErrorBarvType(self, value:'ErrorValueType'):
        GetDllLibPpt().IErrorBarsFormat_set_ErrorBarvType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IErrorBarsFormat_set_ErrorBarvType,self.Ptr, value.value)

    @property

    def ErrorBarSimType(self)->'ErrorBarSimpleType':
        """
        Gets or sets the ErrorBarSimpleType.
            
        """
        GetDllLibPpt().IErrorBarsFormat_get_ErrorBarSimType.argtypes=[c_void_p]
        GetDllLibPpt().IErrorBarsFormat_get_ErrorBarSimType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IErrorBarsFormat_get_ErrorBarSimType,self.Ptr)
        objwraped = ErrorBarSimpleType(ret)
        return objwraped

    @ErrorBarSimType.setter
    def ErrorBarSimType(self, value:'ErrorBarSimpleType'):
        GetDllLibPpt().IErrorBarsFormat_set_ErrorBarSimType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IErrorBarsFormat_set_ErrorBarSimType,self.Ptr, value.value)

    @property
    def ErrorBarVal(self)->float:
        """
        Gets or sets the value of a ErrorBar.
            
        """
        GetDllLibPpt().IErrorBarsFormat_get_ErrorBarVal.argtypes=[c_void_p]
        GetDllLibPpt().IErrorBarsFormat_get_ErrorBarVal.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IErrorBarsFormat_get_ErrorBarVal,self.Ptr)
        return ret

    @ErrorBarVal.setter
    def ErrorBarVal(self, value:float):
        GetDllLibPpt().IErrorBarsFormat_set_ErrorBarVal.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IErrorBarsFormat_set_ErrorBarVal,self.Ptr, value)

    @property
    def MinusVal(self)->float:
        """
        Gets or sets the Minus value of a ErrorBar.
            
        """
        GetDllLibPpt().IErrorBarsFormat_get_MinusVal.argtypes=[c_void_p]
        GetDllLibPpt().IErrorBarsFormat_get_MinusVal.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IErrorBarsFormat_get_MinusVal,self.Ptr)
        return ret

    @MinusVal.setter
    def MinusVal(self, value:float):
        GetDllLibPpt().IErrorBarsFormat_set_MinusVal.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IErrorBarsFormat_set_MinusVal,self.Ptr, value)

    @property
    def PlusVal(self)->float:
        """
        Gets or sets the Plus value of a ErrorBar.
            
        """
        GetDllLibPpt().IErrorBarsFormat_get_PlusVal.argtypes=[c_void_p]
        GetDllLibPpt().IErrorBarsFormat_get_PlusVal.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IErrorBarsFormat_get_PlusVal,self.Ptr)
        return ret

    @PlusVal.setter
    def PlusVal(self, value:float):
        GetDllLibPpt().IErrorBarsFormat_set_PlusVal.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IErrorBarsFormat_set_PlusVal,self.Ptr, value)

    @property
    def ErrorBarNoEndCap(self)->bool:
        """
        Indicates whether the EndCap is shown.
           
        """
        GetDllLibPpt().IErrorBarsFormat_get_ErrorBarNoEndCap.argtypes=[c_void_p]
        GetDllLibPpt().IErrorBarsFormat_get_ErrorBarNoEndCap.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IErrorBarsFormat_get_ErrorBarNoEndCap,self.Ptr)
        return ret

    @ErrorBarNoEndCap.setter
    def ErrorBarNoEndCap(self, value:bool):
        GetDllLibPpt().IErrorBarsFormat_set_ErrorBarNoEndCap.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IErrorBarsFormat_set_ErrorBarNoEndCap,self.Ptr, value)

    @property

    def Line(self)->'IChartGridLine':
        """
        Gets a Line of a ErrorBar.
           
        """
        GetDllLibPpt().IErrorBarsFormat_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IErrorBarsFormat_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IErrorBarsFormat_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


