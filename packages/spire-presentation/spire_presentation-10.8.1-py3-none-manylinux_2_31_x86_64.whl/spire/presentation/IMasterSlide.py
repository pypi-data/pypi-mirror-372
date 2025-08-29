from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IMasterSlide (SpireObject) :
    """
    Represents a master slide in a presentation.
    """
    @property

    def Theme(self)->'Theme':
        """
        Gets the slide's theme.
        
        Returns:
            Theme: Read-only theme object.
        """
        GetDllLibPpt().IMasterSlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_Theme,self.Ptr)
        ret = None if intPtr==None else Theme(intPtr)
        return ret


    @property

    def TitleStyle(self)->'TextStyle':
        """
        Gets text style for title placeholders.
        
        Returns:
            TextStyle: Read-only title text style.
        """
        GetDllLibPpt().IMasterSlide_get_TitleStyle.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_TitleStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_TitleStyle,self.Ptr)
        ret = None if intPtr==None else TextStyle(intPtr)
        return ret


    @property

    def BodyStyle(self)->'TextStyle':
        """
        Gets text style for body placeholders.
        
        Returns:
            TextStyle: Read-only body text style.
        """
        GetDllLibPpt().IMasterSlide_get_BodyStyle.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_BodyStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_BodyStyle,self.Ptr)
        ret = None if intPtr==None else TextStyle(intPtr)
        return ret


    @property

    def OtherStyle(self)->'TextStyle':
        """
        Gets text style for other text elements.
        
        Returns:
            TextStyle: Read-only text style for non-title/body elements.
        """
        GetDllLibPpt().IMasterSlide_get_OtherStyle.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_OtherStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_OtherStyle,self.Ptr)
        ret = None if intPtr==None else TextStyle(intPtr)
        return ret


    @property

    def Shapes(self)->'ShapeCollection':
        """
        Gets all shapes on the slide.
        
        Returns:
            ShapeCollection: Read-only collection of shapes.
        """
        GetDllLibPpt().IMasterSlide_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_Shapes,self.Ptr)
        ret = None if intPtr==None else ShapeCollection(intPtr)
        return ret


    @property

    def Name(self)->str:
        """
        Gets or sets slide name.
        
        Returns:
            str: Name of the master slide.
        """
        GetDllLibPpt().IMasterSlide_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IMasterSlide_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets slide name.
        
        Args:
            value (str): New master slide name.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IMasterSlide_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IMasterSlide_set_Name,self.Ptr,valuePtr)

    @property

    def SlideID(self)->'int':
        """
        Gets unique slide identifier.
        
        Returns:
            int: Read-only slide ID.
        """
        GetDllLibPpt().IMasterSlide_get_SlideID.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_SlideID.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_SlideID,self.Ptr)
        ret = None if intPtr==None else int(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets slide's metadata tags.
        
        Returns:
            TagCollection: Read-only tag collection.
        """
        GetDllLibPpt().IMasterSlide_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Timeline(self)->'TimeLine':
        """
        Gets animation timeline.
        
        Returns:
            TimeLine: Read-only animation timeline object.
        """
        GetDllLibPpt().IMasterSlide_get_Timeline.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_Timeline.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_Timeline,self.Ptr)
        ret = None if intPtr==None else TimeLine(intPtr)
        return ret


    @property

    def SlideShowTransition(self)->'SlideShowTransition':
        """
        Gets slide transition settings.
        
        Returns:
            SlideShowTransition: Read-only transition properties.
        """
        GetDllLibPpt().IMasterSlide_get_SlideShowTransition.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_SlideShowTransition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_SlideShowTransition,self.Ptr)
        ret = None if intPtr==None else SlideShowTransition(intPtr)
        return ret


    @property

    def SlideBackground(self)->'SlideBackground':
        """
        Gets slide background properties.
        
        Returns:
            SlideBackground: Read-only background settings.
        """
        GetDllLibPpt().IMasterSlide_get_SlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_SlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_SlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets parent presentation.
        
        Returns:
            Presentation: Parent presentation object.
        """
        from spire.presentation import Presentation
        GetDllLibPpt().IMasterSlide_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
        Gets parent object.
        
        Returns:
            SpireObject: Read-only parent reference.
        """
        GetDllLibPpt().IMasterSlide_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


#
#    def GetDependingSlides(self)->List['ISlide']:
#        """
#    <summary>
#        Gets an array with all slides, which depend on this master slide.
#    </summary>
#    <returns></returns>
#        """
#        GetDllLibPpt().IMasterSlide_GetDependingSlides.argtypes=[c_void_p]
#        GetDllLibPpt().IMasterSlide_GetDependingSlides.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().IMasterSlide_GetDependingSlides,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, ISlide)
#        return ret



    def ApplyTheme(self ,scheme:'SlideColorScheme'):
        """
        Applies color scheme to the slide.
        
        Args:
            scheme (SlideColorScheme): Color scheme to apply.
        """
        intPtrscheme:c_void_p = scheme.Ptr

        GetDllLibPpt().IMasterSlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().IMasterSlide_ApplyTheme,self.Ptr, intPtrscheme)

    def Dispose(self):
        """Releases resources associated with the object."""
        GetDllLibPpt().IMasterSlide_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IMasterSlide_Dispose,self.Ptr)

    @property

    def Layouts(self)->'IMasterLayouts':
        """
        Gets slide layouts collection.
        
        Returns:
            IMasterLayouts: Collection of slide layouts.
        """
        GetDllLibPpt().IMasterSlide_get_Layouts.argtypes=[c_void_p]
        GetDllLibPpt().IMasterSlide_get_Layouts.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterSlide_get_Layouts,self.Ptr)
        ret = None if intPtr==None else IMasterLayouts(intPtr)
        return ret


