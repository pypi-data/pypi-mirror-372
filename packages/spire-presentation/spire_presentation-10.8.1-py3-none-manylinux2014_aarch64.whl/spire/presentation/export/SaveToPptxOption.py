from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SaveToPptxOption (SpireObject) :
    """
    Represents options for saving presentations to PPTX format.
    Provides configuration settings specific to PPTX output.
    """
    @property
    def SaveToWPS(self)->bool:
        """
        Gets or sets whether to save in WPS Office compatible format.
        
        Returns:
            bool: True for WPS Office compatibility, False for standard PPTX.
        """
        GetDllLibPpt().SaveToPptxOption_get_SaveToWPS.argtypes=[c_void_p]
        GetDllLibPpt().SaveToPptxOption_get_SaveToWPS.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SaveToPptxOption_get_SaveToWPS,self.Ptr)
        return ret

    @SaveToWPS.setter
    def SaveToWPS(self, value:bool):
        """
        Sets whether to save in WPS Office compatible format.
        
        Args:
            value (bool): True for WPS Office compatibility, False for standard PPTX.
        """
        GetDllLibPpt().SaveToPptxOption_set_SaveToWPS.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SaveToPptxOption_set_SaveToWPS,self.Ptr, value)

