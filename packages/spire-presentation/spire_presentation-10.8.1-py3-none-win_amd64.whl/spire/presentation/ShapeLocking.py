from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeLocking (  SimpleShapeBaseLocking) :
    """
    Specifies locking properties for shapes.

    Determines which operations are disabled on parent Autoshape elements,
    particularly focusing on text editing restrictions.
    """
    @property
    def TextEditingProtection(self)->bool:
        """
        Gets or sets text editing restriction status.

        Returns:
            bool: 
            True = Editing text is disabled
            False = Editing text is allowed
        """
        GetDllLibPpt().ShapeLocking_get_TextEditingProtection.argtypes=[c_void_p]
        GetDllLibPpt().ShapeLocking_get_TextEditingProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeLocking_get_TextEditingProtection,self.Ptr)
        return ret

    @TextEditingProtection.setter
    def TextEditingProtection(self, value:bool):
        """
        Sets text editing restriction status.

        Args:
            value (bool): 
            True to disable text editing
            False to allow text editing
        """
        GetDllLibPpt().ShapeLocking_set_TextEditingProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ShapeLocking_set_TextEditingProtection,self.Ptr, value)

