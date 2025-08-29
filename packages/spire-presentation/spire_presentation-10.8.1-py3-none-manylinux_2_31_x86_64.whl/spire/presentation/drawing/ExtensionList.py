from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ExtensionList (SpireObject) :
    """
    Manages extension data for presentation elements (internal use).
    """
    @property
    def IsEmpty(self)->bool:
        """
        Indicates whether the extension list contains any data.
        Returns:
            True if the list is empty; otherwise, False.

        """
        GetDllLibPpt().ExtensionList_get_IsEmpty.argtypes=[c_void_p]
        GetDllLibPpt().ExtensionList_get_IsEmpty.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ExtensionList_get_IsEmpty,self.Ptr)
        return ret

