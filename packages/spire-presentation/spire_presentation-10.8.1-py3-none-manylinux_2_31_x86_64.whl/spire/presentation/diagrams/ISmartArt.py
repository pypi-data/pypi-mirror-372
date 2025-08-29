from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ISmartArt (SpireObject) :
    """
    Represents a SmartArt diagram in a presentation.
    Provides access to SmartArt nodes, color styles, layout types, and styling options.
    Inherits from SpireObject.
    """
    @property

    def Nodes(self)->'ISmartArtNodeCollection':
        """
        Gets the collection of root nodes in the SmartArt diagram.
        Returns:
            ISmartArtNodeCollection: Collection of root nodes.
        """
        GetDllLibPpt().ISmartArt_get_Nodes.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArt_get_Nodes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArt_get_Nodes,self.Ptr)
        ret = None if intPtr==None else ISmartArtNodeCollection(intPtr)
        return ret


    @property

    def ColorStyle(self)->'SmartArtColorType':
        """
        Gets or sets the color style of the SmartArt diagram.
        Returns:
            SmartArtColorType: Current color style.
        """
        GetDllLibPpt().ISmartArt_get_ColorStyle.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArt_get_ColorStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArt_get_ColorStyle,self.Ptr)
        objwraped = SmartArtColorType(ret)
        return objwraped

    @ColorStyle.setter
    def ColorStyle(self, value:'SmartArtColorType'):
        """
        Sets the color style of the SmartArt diagram.
        Args:
            value: SmartArtColorType to apply.
        """
        GetDllLibPpt().ISmartArt_set_ColorStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArt_set_ColorStyle,self.Ptr, value.value)

    @property

    def LayoutType(self)->'SmartArtLayoutType':
        """
        Gets the layout type of the SmartArt diagram (read-only).
        Returns:
            SmartArtLayoutType: Current layout type.
        """
        GetDllLibPpt().ISmartArt_get_LayoutType.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArt_get_LayoutType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArt_get_LayoutType,self.Ptr)
        objwraped = SmartArtLayoutType(ret)
        return objwraped

    @property

    def Style(self)->'SmartArtStyleType':
        """
        Gets or sets the style of the SmartArt diagram.
        Returns:
            SmartArtStyleType: Current style.
        """
        GetDllLibPpt().ISmartArt_get_Style.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArt_get_Style.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArt_get_Style,self.Ptr)
        objwraped = SmartArtStyleType(ret)
        return objwraped

    @Style.setter
    def Style(self, value:'SmartArtStyleType'):
        """
        Sets the style of the SmartArt diagram.
        Args:
            value: SmartArtStyleType to apply.
        """
        GetDllLibPpt().ISmartArt_set_Style.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArt_set_Style,self.Ptr, value.value)

    def Reset(self):
        """
        Resets the SmartArt diagram to its default state.
        """
        GetDllLibPpt().ISmartArt_Reset.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArt_Reset,self.Ptr)

    @property
    def Left(self)->float:
        """
        Gets or sets the x-coordinate of the upper-left corner of the SmartArt.
        Returns:
            float: X-coordinate value.
        """
        GetDllLibPpt().IShape_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        """
        Sets the x-coordinate of the upper-left corner of the SmartArt.
        Args:
            value: New x-coordinate value.
        """
        GetDllLibPpt().IShape_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets the y-coordinate of the upper-left corner of the SmartArt.
        Returns:
            float: Y-coordinate value.
        """
        GetDllLibPpt().IShape_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        """
        Sets the y-coordinate of the upper-left corner of the SmartArt.
        Args:
            value: New y-coordinate value.
        """
        GetDllLibPpt().IShape_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Top,self.Ptr, value)

