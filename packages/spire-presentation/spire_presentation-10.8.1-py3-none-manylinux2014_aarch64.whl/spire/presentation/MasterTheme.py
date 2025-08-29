from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MasterTheme (  Theme) :
    """Represents a master theme containing color, font, and format schemes."""
    @property

    def ColorScheme(self)->'ColorScheme':
        """
        Gets the color scheme for the master theme.
        
        Returns:
            ColorScheme: Read-only color scheme object
        """
        GetDllLibPpt().MasterTheme_get_ColorScheme.argtypes=[c_void_p]
        GetDllLibPpt().MasterTheme_get_ColorScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterTheme_get_ColorScheme,self.Ptr)
        ret = None if intPtr==None else ColorScheme(intPtr)
        return ret


    @property

    def FontScheme(self)->'FontScheme':
        """
        Gets the font scheme for the master theme.
        
        Returns:
            FontScheme: Read-only font scheme object
        """
        GetDllLibPpt().MasterTheme_get_FontScheme.argtypes=[c_void_p]
        GetDllLibPpt().MasterTheme_get_FontScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterTheme_get_FontScheme,self.Ptr)
        ret = None if intPtr==None else FontScheme(intPtr)
        return ret


    @property

    def FormatScheme(self)->'FormatScheme':
        """
        Gets the shape format scheme for the master theme.
        
        Returns:
            FormatScheme: Read-only format scheme object
        """
        GetDllLibPpt().MasterTheme_get_FormatScheme.argtypes=[c_void_p]
        GetDllLibPpt().MasterTheme_get_FormatScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterTheme_get_FormatScheme,self.Ptr)
        ret = None if intPtr==None else FormatScheme(intPtr)
        return ret


    @property

    def SlideColorSchemes(self)->'SlideColorSchemeCollection':
        """
        Gets additional color schemes that can be applied to slides.
        
        Returns:
            SlideColorSchemeCollection: Read-only collection of color schemes
        """
        GetDllLibPpt().MasterTheme_get_SlideColorSchemes.argtypes=[c_void_p]
        GetDllLibPpt().MasterTheme_get_SlideColorSchemes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterTheme_get_SlideColorSchemes,self.Ptr)
        ret = None if intPtr==None else SlideColorSchemeCollection(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current MasterTheme is equal to another object.
        
        Args:
            obj (SpireObject): The object to compare with
            
        Returns:
            bool: True if equal, otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().MasterTheme_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().MasterTheme_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().MasterTheme_Equals,self.Ptr, intPtrobj)
        return ret

