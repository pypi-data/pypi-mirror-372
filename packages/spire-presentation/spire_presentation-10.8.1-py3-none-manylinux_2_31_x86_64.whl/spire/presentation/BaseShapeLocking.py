from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BaseShapeLocking (  PptObject) :
    """
    Base class for shape locking configurations.
    
    Attributes:
        HasLocks (bool): Indicates if locks are applied to the shape.
    """
    @property
    def HasLocks(self)->bool:
       
        """Checks if any locking properties are set on the shape."""
     
        GetDllLibPpt().BaseShapeLocking_get_HasLocks.argtypes=[c_void_p]
        GetDllLibPpt().BaseShapeLocking_get_HasLocks.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().BaseShapeLocking_get_HasLocks,self.Ptr)
        return ret

