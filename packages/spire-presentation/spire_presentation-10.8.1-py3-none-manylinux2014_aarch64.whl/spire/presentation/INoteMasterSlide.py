from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class INoteMasterSlide (SpireObject) :
    """
    Represents a notes master slide in a presentation. 
    Provides properties and methods to manage theme, shapes, background, 
    transitions, and other slide-level attributes.
    """
    @property

    def Theme(self)->'Theme':
        """
        Gets the slide's theme.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Theme,self.Ptr)
        ret = None if intPtr==None else Theme(intPtr)
        return ret


    @property

    def Shapes(self)->'ShapeCollection':
        """
        Gets the shapes of the slide.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Shapes,self.Ptr)
        ret = None if intPtr==None else ShapeCollection(intPtr)
        return ret


    @property

    def Name(self)->str:
        """
        Gets or sets the name of the slide.
        Read/write.
        """
        GetDllLibPpt().INoteMasterSlide_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().INoteMasterSlide_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().INoteMasterSlide_set_Name,self.Ptr,valuePtr)

    @property

    def SlideID(self)->'UInt32':
        """
        Gets the unique ID of the slide.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_SlideID.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_SlideID.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_SlideID,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the slide's tags collection.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Timeline(self)->'TimeLine':
        """
        Gets animation timeline object.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_Timeline.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Timeline.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Timeline,self.Ptr)
        ret = None if intPtr==None else TimeLine(intPtr)
        return ret


    @property

    def SlideShowTransition(self)->'SlideShowTransition':
        """
        Gets transition settings for the slide show.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_SlideShowTransition.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_SlideShowTransition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_SlideShowTransition,self.Ptr)
        ret = None if intPtr==None else SlideShowTransition(intPtr)
        return ret


    @property

    def SlideBackground(self)->'SlideBackground':
        """
        Gets the slide's background properties.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_SlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_SlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_SlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
        Reference to parent object.
        Read-only.
        """
        GetDllLibPpt().INoteMasterSlide_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def ApplyTheme(self ,scheme:'SlideColorScheme'):
        """
        Applies an extra color scheme to the slide.

        Args:
            scheme: Color scheme to apply
        """
        intPtrscheme:c_void_p = scheme.Ptr

        GetDllLibPpt().INoteMasterSlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().INoteMasterSlide_ApplyTheme,self.Ptr, intPtrscheme)

    def Dispose(self):
        """
        Releases resources associated with the object.
        """
        GetDllLibPpt().INoteMasterSlide_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().INoteMasterSlide_Dispose,self.Ptr)

