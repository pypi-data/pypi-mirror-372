from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class RelativeRectangle (SpireObject) :
    """
    Represents a rectangle defined using relative coordinates (percentages).
    
    Used to specify positions and dimensions relative to a container element,
    with values typically ranging from 0.0 to 100.0.
    """
    @property
    def X(self)->float:
        """
        Gets the X-coordinate of the rectangle's origin.
        
        Returns:
            float: The relative X-position as a percentage.
        """
        GetDllLibPpt().RelativeRectangle_get_X.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_X.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_X,self.Ptr)
        return ret

    @X.setter
    def X(self, value:float):
        """
        Sets the X-coordinate of the rectangle's origin.
        
        Args:
            value: The relative X-position percentage to set.
        """
        GetDllLibPpt().RelativeRectangle_set_X.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_X,self.Ptr, value)

    @property
    def Y(self)->float:
        """
        Gets the Y-coordinate of the rectangle's origin.
        
        Returns:
            float: The relative Y-position as a percentage.
        """
        GetDllLibPpt().RelativeRectangle_get_Y.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Y.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Y,self.Ptr)
        return ret

    @Y.setter
    def Y(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Y.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Y,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets the Width of the rectangle.
        
        Returns:
            float: The relative Width as a percentage.
        """
        GetDllLibPpt().RelativeRectangle_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets the Height of the rectangle.
        
        Returns:
            float: The relative Height as a percentage.
        """
        GetDllLibPpt().RelativeRectangle_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Height,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Sets the Left of the rectangle.
        
        Args:
            value: The relative Left percentage to set.
        """
        GetDllLibPpt().RelativeRectangle_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets the Top of the rectangle.
        
        Returns:
            float: The relative Top as a percentage.
        """
        GetDllLibPpt().RelativeRectangle_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Top,self.Ptr, value)

    @property
    def Right(self)->float:
        """
        Gets the Right of the rectangle.
        
        Returns:
            float: The relative Right as a percentage.
        """
        GetDllLibPpt().RelativeRectangle_get_Right.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Right.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Right,self.Ptr)
        return ret

    @Right.setter
    def Right(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Right.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Right,self.Ptr, value)

    @property
    def Bottom(self)->float:
        """
        Gets the Bottom of the rectangle.
        
        Returns:
            float: The relative Bottom as a percentage.
        """
        GetDllLibPpt().RelativeRectangle_get_Bottom.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Bottom.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Bottom,self.Ptr)
        return ret

    @Bottom.setter
    def Bottom(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Bottom.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Bottom,self.Ptr, value)

    @dispatch

    def Transform(self ,rect:RectangleF)->RectangleF:
        """
        Transforms a RectangleF using the current relative rectangle values.
        
        Args:
            rect: The source rectangle to transform.
        
        Returns:
            RectangleF: The transformed rectangle.
        """
        intPtrrect:c_void_p = rect.Ptr

        GetDllLibPpt().RelativeRectangle_Transform.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().RelativeRectangle_Transform.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RelativeRectangle_Transform,self.Ptr, intPtrrect)
        ret = None if intPtr==None else RectangleF(intPtr)
        return ret


    @dispatch

    def Transform(self ,rect:'RelativeRectangle')->'RelativeRectangle':
        """
        Transforms another RelativeRectangle using the current relative rectangle values.
        
        Args:
            rect: The source relative rectangle to transform.
        
        Returns:
            RelativeRectangle: The transformed relative rectangle.
        """
        intPtrrect:c_void_p = rect.Ptr

        GetDllLibPpt().RelativeRectangle_TransformR.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().RelativeRectangle_TransformR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RelativeRectangle_TransformR,self.Ptr, intPtrrect)
        ret = None if intPtr==None else RelativeRectangle(intPtr)
        return ret


