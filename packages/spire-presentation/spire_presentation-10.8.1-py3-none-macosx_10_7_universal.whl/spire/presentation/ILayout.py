from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ILayout (ActiveSlide) :
    """
    Represents a layout slide within a presentation.
    """
    @property

    def LayoutType(self)->'SlideLayoutType':
        """
        Gets the layout type of this layout slide.

        Returns:
            SlideLayoutType: The type of the slide layout.
        """
        GetDllLibPpt().ILayout_get_LayoutType.argtypes=[c_void_p]
        GetDllLibPpt().ILayout_get_LayoutType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ILayout_get_LayoutType,self.Ptr)
        objwraped = SlideLayoutType(ret)
        return objwraped

#
#    def GetDependingSlides(self)->List['ISlide']:
#        """
#    <summary>
#         Gets an array with all slides, which depend on this layout slide.
#    </summary>
#        """
#        GetDllLibPpt().ILayout_GetDependingSlides.argtypes=[c_void_p]
#        GetDllLibPpt().ILayout_GetDependingSlides.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ILayout_GetDependingSlides,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, ISlide)
#        return ret


    @property

    def Name(self)->str:
        """
        Gets or sets the name of the layout.

        Returns:
            str: The name of the layout.
        """
        GetDllLibPpt().ILayout_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ILayout_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ILayout_get_Name,self.Ptr))
        return ret
    
    @Name.setter
    def Name(self, value:str):
        """
        Sets the name of the layout.

        Args:
            value (str): The new name for the layout.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ActiveSlide_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ActiveSlide_set_Name,self.Ptr,valuePtr)


    @property
    def Shapes(self)->'ShapeCollection':
        """
        Gets the shapes collection of the slide.

        Returns:
            ShapeCollection: Read-only collection of shapes on the slide.
        """
        GetDllLibPpt().ActiveSlide_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Shapes,self.Ptr)
        ret = None if intPtr==None else ShapeCollection(intPtr)
        return ret

    
    def InsertPlaceholder(self,type:'InsertPlaceholderType',rectangle:'RectangleF')->'IAutoShape':
        """
        Inserts a placeholder shape at the specified position.

        Args:
            type (InsertPlaceholderType): Type of placeholder to insert.
            rectangle (RectangleF): Position and dimensions of the placeholder.

        Returns:
            IAutoShape: The newly created placeholder shape.
        """
        
        enumtype:c_int = type.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ILayout_InsertPlaceholder.argtypes=[c_void_p,c_int,c_void_p]
        GetDllLibPpt().ILayout_InsertPlaceholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ILayout_InsertPlaceholder,self.Ptr,enumtype,intPtrrectangle)
        ret = None if intPtr==None else IAutoShape(intPtr)
        return ret
    
    def SaveAsImage(self)->'Stream':
        """
        Renders the layout slide as an image stream.

        Returns:
            Stream: Image data stream.
        """
        GetDllLibPpt().ILayout_SaveAsImage.argtypes=[c_void_p]
        GetDllLibPpt().ILayout_SaveAsImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ILayout_SaveAsImage,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret
    

    @property

    def ShowMasterShapes(self)->bool:
        """
        Determines whether master shapes should be displayed.

        Returns:
            bool: True if master shapes should be visible.
        """
        GetDllLibPpt().ILayout_get_ShowMasterShapes.argtypes=[c_void_p]
        GetDllLibPpt().ILayout_get_ShowMasterShapes.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ILayout_get_ShowMasterShapes,self.Ptr)
        return ret
    
    @ShowMasterShapes.setter
    def ShowMasterShapes(self, value:bool):
        """
        Sets whether master shapes should be displayed.

        Args:
            value (bool): True to show master shapes, False to hide them.
        """
        GetDllLibPpt().ILayout_set_ShowMasterShapes.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ILayout_set_ShowMasterShapes,self.Ptr,value)
    
