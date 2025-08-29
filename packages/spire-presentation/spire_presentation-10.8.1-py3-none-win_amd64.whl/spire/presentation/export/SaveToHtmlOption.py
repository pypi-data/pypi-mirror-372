from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SaveToHtmlOption (SpireObject) :
    """
    Represents configuration options for saving presentations as HTML.
    Inherits from: SpireObject class
    """
    @property
    def Center(self)->bool:
        """
        Gets or sets whether to center-align content in HTML output.

        Returns:
            bool: True if content should be centered, False otherwise.
        """
        GetDllLibPpt().SaveToHtmlOption_get_Center.argtypes=[c_void_p]
        GetDllLibPpt().SaveToHtmlOption_get_Center.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SaveToHtmlOption_get_Center,self.Ptr)
        return ret

    @Center.setter
    def Center(self, value:bool):
        """
        Sets whether to center-align content in HTML output.

        Args:
            value (bool): True to center content, False otherwise.
        """
        GetDllLibPpt().SaveToHtmlOption_set_Center.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SaveToHtmlOption_set_Center,self.Ptr, value)

