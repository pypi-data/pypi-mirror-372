from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Theme (  IActivePresentation) :
    """
    Represents a theme with color schemes, font schemes, and format schemes.

    """
    @property

    def Name(self)->str:
        """
        Gets or sets the name of the theme.

        Returns:
            str: Current name of the theme.
        """
        GetDllLibPpt().Theme_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().Theme_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Theme_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets the name of the theme.

        Args:
            value (str): New name to set.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Theme_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Theme_set_Name,self.Ptr,valuePtr)

    @property

    def ColorScheme(self)->'ColorScheme':
        """
        Gets the color scheme of the theme.

        Returns:
            ColorScheme: Current color scheme.
        """
        GetDllLibPpt().Theme_get_ColorScheme.argtypes=[c_void_p]
        GetDllLibPpt().Theme_get_ColorScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Theme_get_ColorScheme,self.Ptr)
        ret = None if intPtr==None else ColorScheme(intPtr)
        return ret


    @property

    def FontScheme(self)->'FontScheme':
        """
        Gets the shape format scheme.

        Returns:
            FormatScheme: Current format scheme.
        """
        GetDllLibPpt().Theme_get_FontScheme.argtypes=[c_void_p]
        GetDllLibPpt().Theme_get_FontScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Theme_get_FontScheme,self.Ptr)
        ret = None if intPtr==None else FontScheme(intPtr)
        return ret


    @property

    def FormatScheme(self)->'FormatScheme':
        """
        Gets the parent presentation.

        Returns:
            Presentation: Parent presentation object.
        """
        GetDllLibPpt().Theme_get_FormatScheme.argtypes=[c_void_p]
        GetDllLibPpt().Theme_get_FormatScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Theme_get_FormatScheme,self.Ptr)
        ret = None if intPtr==None else FormatScheme(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Determines if this theme equals another object.

        Args:
            obj (SpireObject): Object to compare with.

        Returns:
            bool: True if objects are equal, False otherwise.
        """
        GetDllLibPpt().Theme_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().Theme_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Theme_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Theme_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Theme_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Theme_Equals,self.Ptr, intPtrobj)
        return ret

