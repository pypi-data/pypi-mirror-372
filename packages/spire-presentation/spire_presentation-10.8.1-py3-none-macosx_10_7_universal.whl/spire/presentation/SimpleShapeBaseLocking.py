from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SimpleShapeBaseLocking (  BaseShapeLocking) :
    """
    Provides locking properties for simple shapes in presentations.
    
    This class allows controlling various protection settings that determine
    which operations are disabled on parent Autoshape elements.
    """
    @property
    def GroupingProtection(self)->bool:
        """
        Gets or sets whether adding this shape to groups is disallowed.
        
        Returns:
            bool: 
            True = Adding to groups is disabled
            False = Adding to groups is allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_GroupingProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_GroupingProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_GroupingProtection,self.Ptr)
        return ret

    @GroupingProtection.setter
    def GroupingProtection(self, value:bool):
        """
        Sets whether adding this shape to groups is disallowed.
        
        Args:
            value (bool): 
            True to disable adding to groups
            False to allow adding to groups
        """
        GetDllLibPpt().SimpleShapeBaseLocking_set_GroupingProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_GroupingProtection,self.Ptr, value)

    @property
    def SelectionProtection(self)->bool:
        """
        Gets or sets whether selecting this shape is disallowed.
        
        Returns:
            bool: 
            True = Selecting is disabled
            False = Selecting is allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_SelectionProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_SelectionProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_SelectionProtection,self.Ptr)
        return ret

    @SelectionProtection.setter
    def SelectionProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_SelectionProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_SelectionProtection,self.Ptr, value)

    @property
    def RotationProtection(self)->bool:
        """
        Gets or sets whether changing rotation angle is disallowed.
        
        Returns:
            bool: 
            True = Rotation changes are disabled
            False = Rotation changes are allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_RotationProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_RotationProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_RotationProtection,self.Ptr)
        return ret

    @RotationProtection.setter
    def RotationProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_RotationProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_RotationProtection,self.Ptr, value)

    @property
    def AspectRatioProtection(self)->bool:
        """
        Gets or sets whether preserving aspect ratio on resize is enforced.
        
        Returns:
            bool: 
            True = Aspect ratio must be preserved
            False = Aspect ratio can be changed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_AspectRatioProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_AspectRatioProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_AspectRatioProtection,self.Ptr)
        return ret

    @AspectRatioProtection.setter
    def AspectRatioProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_AspectRatioProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_AspectRatioProtection,self.Ptr, value)

    @property
    def PositionProtection(self)->bool:
        """
        Gets or sets whether moving this shape is disallowed.
        
        Returns:
            bool: 
            True = Moving is disabled
            False = Moving is allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_PositionProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_PositionProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_PositionProtection,self.Ptr)
        return ret

    @PositionProtection.setter
    def PositionProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_PositionProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_PositionProtection,self.Ptr, value)

    @property
    def ResizeProtection(self)->bool:
        """
        Gets or sets whether resizing this shape is disallowed.
        
        Returns:
            bool: 
            True = Resizing is disabled
            False = Resizing is allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_ResizeProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_ResizeProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_ResizeProtection,self.Ptr)
        return ret

    @ResizeProtection.setter
    def ResizeProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_ResizeProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_ResizeProtection,self.Ptr, value)

    @property
    def EditPointProtection(self)->bool:
        """
        Gets or sets whether direct contour editing is disallowed.
        
        Returns:
            bool: 
            True = Contour editing is disabled
            False = Contour editing is allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_EditPointProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_EditPointProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_EditPointProtection,self.Ptr)
        return ret

    @EditPointProtection.setter
    def EditPointProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_EditPointProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_EditPointProtection,self.Ptr, value)

    @property
    def AdjustHandlesProtection(self)->bool:
        """
        Gets or sets whether changing adjust values is disallowed.
        
        Returns:
            bool: 
            True = Adjust handle changes are disabled
            False = Adjust handle changes are allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_AdjustHandlesProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_AdjustHandlesProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_AdjustHandlesProtection,self.Ptr)
        return ret

    @AdjustHandlesProtection.setter
    def AdjustHandlesProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_AdjustHandlesProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_AdjustHandlesProtection,self.Ptr, value)

    @property
    def ArrowheadChangesProtection(self)->bool:
        """
        Gets or sets whether changing arrowheads is disallowed.
        
        Returns:
            bool: 
            True = Arrowhead changes are disabled
            False = Arrowhead changes are allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_ArrowheadChangesProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_ArrowheadChangesProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_ArrowheadChangesProtection,self.Ptr)
        return ret

    @ArrowheadChangesProtection.setter
    def ArrowheadChangesProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_ArrowheadChangesProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_ArrowheadChangesProtection,self.Ptr, value)

    @property
    def ShapeTypeProtection(self)->bool:
        """
        Gets or sets whether changing shape type is disallowed.
        
        Returns:
            bool: 
            True = Shape type changes are disabled
            False = Shape type changes are allowed
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_ShapeTypeProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_ShapeTypeProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_ShapeTypeProtection,self.Ptr)
        return ret

    @ShapeTypeProtection.setter
    def ShapeTypeProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_ShapeTypeProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_ShapeTypeProtection,self.Ptr, value)

