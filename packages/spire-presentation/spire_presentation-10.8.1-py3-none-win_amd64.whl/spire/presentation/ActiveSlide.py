from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ActiveSlide (  PptObject, IActiveSlide) :
    """
    Represents common slide types in a presentation.
    Provides access to slide content, properties, and formatting.
    """
    @property

    def Shapes(self)->'ShapeCollection':
        """
        Gets the collection of shapes on the slide.

        Returns:
            ShapeCollection: Read-only collection of shapes.
        """
        GetDllLibPpt().ActiveSlide_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Shapes,self.Ptr)
        ret = None if intPtr==None else ShapeCollection(intPtr)
        return ret


    @property

    def Name(self)->str:
        """
        Gets or sets the name of the slide.

        Returns:
            str: The name of the slide.
        """
        GetDllLibPpt().ActiveSlide_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ActiveSlide_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ActiveSlide_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ActiveSlide_set_Name,self.Ptr,valuePtr)

    @property

    def SlideID(self)->'int':
        """
        Gets the unique identifier of the slide.

        Returns:
            int: Read-only unique identifier of the slide.
        """
        GetDllLibPpt().ActiveSlide_get_SlideID.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_SlideID.restype=c_void_p
        slidId = CallCFunction(GetDllLibPpt().ActiveSlide_get_SlideID,self.Ptr)
        return slidId


    #@SlideID.setter
    #def SlideID(self, value:'UInt32'):
    #    GetDllLibPpt().ActiveSlide_set_SlideID.argtypes=[c_void_p, c_void_p]
    #    CallCFunction(GetDllLibPpt().ActiveSlide_set_SlideID,self.Ptr, value.Ptr)

    @property

    def Theme(self)->'Theme':
        """
        Gets the theme associated with this slide.

        Returns:
            Theme: The theme applied to this slide.
        """
        GetDllLibPpt().ActiveSlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Theme,self.Ptr)
        ret = None if intPtr==None else Theme(intPtr)
        return ret



    def ApplyTheme(self ,scheme:'SlideColorScheme'):
        """
        Applies an additional color scheme to the slide.

        Args:
            scheme: Color scheme to apply to the slide.
        """
        intPtrscheme:c_void_p = scheme.Ptr

        GetDllLibPpt().ActiveSlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ActiveSlide_ApplyTheme,self.Ptr, intPtrscheme)

    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the collection of tags associated with the slide.

        Returns:
            TagCollection: Read-only collection of tags.
        """
        GetDllLibPpt().ActiveSlide_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Timeline(self)->'TimeLine':
        """
        Gets the animation timeline for the slide.

        Returns:
            TimeLine: Read-only animation timeline object.
        """
        from spire.presentation.animation.TimeLine import TimeLine
        GetDllLibPpt().ActiveSlide_get_Timeline.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Timeline.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Timeline,self.Ptr)
        ret = None if intPtr==None else TimeLine(intPtr)
        return ret


    @property

    def SlideShowTransition(self)->'SlideShowTransition':
        """
        Gets transition settings for the slide during a slideshow.

        Returns:
            SlideShowTransition: Read-only transition settings object.
        """
        GetDllLibPpt().ActiveSlide_get_SlideShowTransition.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_SlideShowTransition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_SlideShowTransition,self.Ptr)
        ret = None if intPtr==None else SlideShowTransition(intPtr)
        return ret


    @property

    def SlideBackground(self)->'SlideBackground':
        """
        Gets the background settings of the slide.

        Returns:
            SlideBackground: Read-only background settings object.
        """
        GetDllLibPpt().ActiveSlide_get_SlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_SlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_SlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def DisplaySlideBackground(self)->'SlideBackground':
        """
        Gets the effective background settings displayed for the slide.

        Returns:
            SlideBackground: Read-only background settings object.
        """
        GetDllLibPpt().ActiveSlide_get_DisplaySlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_DisplaySlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_DisplaySlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current slide.

        Args:
            obj: The object to compare with the current slide.

        Returns:
            bool: True if the objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ActiveSlide_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ActiveSlide_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ActiveSlide_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation that contains this slide.

        Returns:
            Presentation: The parent presentation object.
        """
        from spire.presentation import Presentation
        GetDllLibPpt().ActiveSlide_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


