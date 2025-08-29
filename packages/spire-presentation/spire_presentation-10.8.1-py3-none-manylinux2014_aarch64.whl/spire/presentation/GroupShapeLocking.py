from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GroupShapeLocking (  BaseShapeLocking) :
    """
    Indicates which operations are disabled on the parent GroupShape.
    """
    @property
    def GroupingProtection(self)->bool:
        """
        Indicates whether an adding this shape to a group Disallow.
        """
        GetDllLibPpt().GroupShapeLocking_get_GroupingProtection.argtypes=[c_void_p]
        GetDllLibPpt().GroupShapeLocking_get_GroupingProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GroupShapeLocking_get_GroupingProtection,self.Ptr)
        return ret

    @GroupingProtection.setter
    def GroupingProtection(self, value:bool):
        GetDllLibPpt().GroupShapeLocking_set_GroupingProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GroupShapeLocking_set_GroupingProtection,self.Ptr, value)

    @property
    def UngroupingProtection(self)->bool:
        """
        Indicates whether splitting this groupshape Disallow.
        """
        GetDllLibPpt().GroupShapeLocking_get_UngroupingProtection.argtypes=[c_void_p]
        GetDllLibPpt().GroupShapeLocking_get_UngroupingProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GroupShapeLocking_get_UngroupingProtection,self.Ptr)
        return ret

    @UngroupingProtection.setter
    def UngroupingProtection(self, value:bool):
        GetDllLibPpt().GroupShapeLocking_set_UngroupingProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GroupShapeLocking_set_UngroupingProtection,self.Ptr, value)

    @property
    def SelectionProtection(self)->bool:
        """
        Indicates whether a selecting this shape Disallow.
    
        """
        GetDllLibPpt().GroupShapeLocking_get_SelectionProtection.argtypes=[c_void_p]
        GetDllLibPpt().GroupShapeLocking_get_SelectionProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GroupShapeLocking_get_SelectionProtection,self.Ptr)
        return ret

    @SelectionProtection.setter
    def SelectionProtection(self, value:bool):
        GetDllLibPpt().GroupShapeLocking_set_SelectionProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GroupShapeLocking_set_SelectionProtection,self.Ptr, value)

    @property
    def RotationProtection(self)->bool:
        """
        Indicates whether a changing rotation angle of this shape Disallow.
   
        """
        GetDllLibPpt().GroupShapeLocking_get_RotationProtection.argtypes=[c_void_p]
        GetDllLibPpt().GroupShapeLocking_get_RotationProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GroupShapeLocking_get_RotationProtection,self.Ptr)
        return ret

    @RotationProtection.setter
    def RotationProtection(self, value:bool):
        GetDllLibPpt().GroupShapeLocking_set_RotationProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GroupShapeLocking_set_RotationProtection,self.Ptr, value)

    @property
    def AspectRatioProtection(self)->bool:
        """
        Indicates whether a shape have to preserve aspect ratio on resizing.
    
        """
        GetDllLibPpt().GroupShapeLocking_get_AspectRatioProtection.argtypes=[c_void_p]
        GetDllLibPpt().GroupShapeLocking_get_AspectRatioProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GroupShapeLocking_get_AspectRatioProtection,self.Ptr)
        return ret

    @AspectRatioProtection.setter
    def AspectRatioProtection(self, value:bool):
        GetDllLibPpt().GroupShapeLocking_set_AspectRatioProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GroupShapeLocking_set_AspectRatioProtection,self.Ptr, value)

    @property
    def PositionProtection(self)->bool:
        """
        Indicates whether a moving this shape Disallow.
    
        """
        GetDllLibPpt().GroupShapeLocking_get_PositionProtection.argtypes=[c_void_p]
        GetDllLibPpt().GroupShapeLocking_get_PositionProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GroupShapeLocking_get_PositionProtection,self.Ptr)
        return ret

    @PositionProtection.setter
    def PositionProtection(self, value:bool):
        GetDllLibPpt().GroupShapeLocking_set_PositionProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GroupShapeLocking_set_PositionProtection,self.Ptr, value)

    @property
    def ResizeProtection(self)->bool:
        """
        Indicates whether a resizing this shape Disallow.
    
        """
        GetDllLibPpt().GroupShapeLocking_get_ResizeProtection.argtypes=[c_void_p]
        GetDllLibPpt().GroupShapeLocking_get_ResizeProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GroupShapeLocking_get_ResizeProtection,self.Ptr)
        return ret

    @ResizeProtection.setter
    def ResizeProtection(self, value:bool):
        GetDllLibPpt().GroupShapeLocking_set_ResizeProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GroupShapeLocking_set_ResizeProtection,self.Ptr, value)

