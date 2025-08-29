from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OleObject (  IActiveSlide, IActivePresentation) :
    """
    Represents an embedded OLE (Object Linking and Embedding) object.
    
    Inherits from both IActiveSlide and IActivePresentation interfaces.
    """
    @property

    def Name(self)->str:
        """
        Gets the name identifier of the OLE object.
        
        Returns:
            str: Read-only name of the control.
        """
        GetDllLibPpt().OleObject_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().OleObject_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().OleObject_get_Name,self.Ptr))
        return ret


    @property

    def PictureFill(self)->'PictureFillFormat':
        """
        Gets image fill properties for the OLE object's preview.
        
        Returns:
            PictureFillFormat: Read-only image fill properties.
        """
        GetDllLibPpt().OleObject_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().OleObject_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObject_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets or sets the graphical frame container.
        
        Returns:
            GraphicFrame: Current frame container for the OLE object.
        """
        GetDllLibPpt().OleObject_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().OleObject_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObject_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        """
        Sets the graphical frame container.
        
        Args:
            value: New frame container to apply.
        """
        GetDllLibPpt().OleObject_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().OleObject_set_Frame,self.Ptr, value.Ptr)

    @property

    def Properties(self)->'OleObjectProperties':
        """
        Gets collection of OLE-specific properties.
        
        Returns:
            OleObjectProperties: Read-only collection of OLE properties.
        """
        GetDllLibPpt().OleObject_get_Properties.argtypes=[c_void_p]
        GetDllLibPpt().OleObject_get_Properties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObject_get_Properties,self.Ptr)
        ret = None if intPtr==None else OleObjectProperties(intPtr)
        return ret
    
    @property

    def ShapeID(self)->'UInt16':
        """
        Gets the unique shape identifier.
        
        Returns:
            UInt16: Read-only shape identifier.
        """
        GetDllLibPpt().OleObject_get_ShapeID.argtypes=[c_void_p]
        GetDllLibPpt().OleObject_get_ShapeID.restype=c_void_p
        ret = CallCFunction(GetDllLibPpt().OleObject_get_ShapeID,self.Ptr)
        return ret
    
    @property

    def IsHidden(self)->'bool':
        """
        Gets or sets the visibility state.
        
        Returns:
            bool: Current visibility status (True = hidden).
        """
        GetDllLibPpt().OleObject_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().OleObject_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OleObject_get_IsHidden,self.Ptr)
        return ret


    @IsHidden.setter
    def IsHidden(self, value:'bool'):
        """
        Sets the visibility state.
        
        Args:
            value: New visibility status (True = hidden).
        """
        GetDllLibPpt().OleObject_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().OleObject_set_IsHidden,self.Ptr, value)


