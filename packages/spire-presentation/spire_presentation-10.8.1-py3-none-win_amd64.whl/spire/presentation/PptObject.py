from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PptObject (SpireObject) :
    """
    Represents a base PowerPoint object providing common functionality for parent object 
    access and resource management. Inherits from SpireObject.
    """
    @property

    def Parent(self)->'SpireObject':
        """
        Gets the parent object of the current PowerPoint object.

        Returns:
            SpireObject: Reference to the parent object (read-only).
        """
        GetDllLibPpt().PptObject_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().PptObject_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PptObject_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def Dispose(self):
        """
        Releases all resources used by the PptObject.

        This method should be called to free unmanaged resources when the object is 
        no longer needed to prevent memory leaks.
        """
        GetDllLibPpt().PptObject_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().PptObject_Dispose,self.Ptr)

