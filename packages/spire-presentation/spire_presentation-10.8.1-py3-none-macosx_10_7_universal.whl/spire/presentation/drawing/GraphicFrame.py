from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GraphicFrame (SpireObject) :
    """Represents shape frame's properties."""
    @dispatch
    def __init__(self):
        """Initializes a new instance of GraphicFrame with default values."""
        GetDllLibPpt().GraphicFrame_Create_noagrs.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GraphicFrame_Create_noagrs)
        super(GraphicFrame, self).__init__(intPtr)

    @dispatch
    def __init__(self,left:float,top:float,width:float,height:float,hflip:bool,vfilp:bool,rotation:float):
        """
        Initializes a new instance of GraphicFrame with specified parameters.
        
        Args:
            left: X coordinate of upper-left corner
            top: Y coordinate of upper-left corner
            width: Frame width
            height: Frame height
            hflip: Horizontal flip status
            vfilp: Vertical flip status
            rotation: Rotation angle in degrees
        """
        GetDllLibPpt().GraphicFrame_Create.argtypes=[c_float, c_float, c_float, c_float, c_bool, c_bool, c_float]
        GetDllLibPpt().GraphicFrame_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GraphicFrame_Create,left,top,width,height,hflip,vfilp,rotation)
        super(GraphicFrame, self).__init__(intPtr)
   
    @property
    def Left(self)->float:
        """Gets the X coordinate of the upper-left corner of a frame. Read-only."""
        GetDllLibPpt().GraphicFrame_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_Left,self.Ptr)
        return ret

    @property
    def Top(self)->float:
        """Gets the Y coordinate of the upper-left corner of a frame. Read-only."""
        GetDllLibPpt().GraphicFrame_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_Top,self.Ptr)
        return ret

    @property
    def Width(self)->float:
        """Gets the width of a frame. Read-only."""
        GetDllLibPpt().GraphicFrame_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().GraphicFrame_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().GraphicFrame_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """Gets the height of a frame. Read-only."""
        GetDllLibPpt().GraphicFrame_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_Height,self.Ptr)
        return ret

    @property
    def Rotation(self)->float:
        """Gets the number of degrees a frame is rotated around the z-axis. Read-only."""
        GetDllLibPpt().GraphicFrame_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        """Sets the rotation angle around the z-axis in degrees."""
        GetDllLibPpt().GraphicFrame_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().GraphicFrame_set_Rotation,self.Ptr, value)

    @property
    def CenterX(self)->float:
        """Gets the X coordinate of a frame's center. Read-only."""
        GetDllLibPpt().GraphicFrame_get_CenterX.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_CenterX.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_CenterX,self.Ptr)
        return ret

    @property
    def CenterY(self)->float:
        """Gets the Y coordinate of a frame's center. Read-only."""
        GetDllLibPpt().GraphicFrame_get_CenterY.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_CenterY.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_CenterY,self.Ptr)
        return ret

    @property
    def IsFlipX(self)->bool:
        """Indicates whether a frame is flipped horizontally. Read-only."""
        GetDllLibPpt().GraphicFrame_get_IsFlipX.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_IsFlipX.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_IsFlipX,self.Ptr)
        return ret

    @IsFlipX.setter
    def IsFlipX(self, value:bool):
        GetDllLibPpt().GraphicFrame_set_IsFlipX.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GraphicFrame_set_IsFlipX,self.Ptr, value)

    @property
    def IsFlipY(self)->bool:
        """Indicates whether a frame is flipped vertically. Read-only."""
        GetDllLibPpt().GraphicFrame_get_IsFlipY.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_IsFlipY.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_get_IsFlipY,self.Ptr)
        return ret

    @IsFlipY.setter
    def IsFlipY(self, value:bool):
        GetDllLibPpt().GraphicFrame_set_IsFlipY.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GraphicFrame_set_IsFlipY,self.Ptr, value)

    @property

    def Rectangle(self)->'RectangleF':
        """Gets the coordinates of a frame. Read-only."""
        GetDllLibPpt().GraphicFrame_get_Rectangle.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_get_Rectangle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GraphicFrame_get_Rectangle,self.Ptr)
        ret = None if intPtr==None else RectangleF(intPtr)
        return ret


    @dispatch

    def Equals(self ,obj:SpireObject)->bool:
        """
        Determines whether the current GraphicFrame is equal to another object.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GraphicFrame_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GraphicFrame_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_Equals,self.Ptr, intPtrobj)
        return ret

    @dispatch

    def Equals(self ,value:'GraphicFrame')->bool:
        """
        Determines whether the current GraphicFrame is equal to another GraphicFrame.
        
        Args:
            value (GraphicFrame): The GraphicFrame to compare with.
            
        Returns:
            bool: True if objects are equal, otherwise False.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().GraphicFrame_EqualsV.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GraphicFrame_EqualsV.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_EqualsV,self.Ptr, intPtrvalue)
        return ret

    def GetHashCode(self)->int:
        """Gets a hash code for this object."""
        GetDllLibPpt().GraphicFrame_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().GraphicFrame_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GraphicFrame_GetHashCode,self.Ptr)
        return ret

