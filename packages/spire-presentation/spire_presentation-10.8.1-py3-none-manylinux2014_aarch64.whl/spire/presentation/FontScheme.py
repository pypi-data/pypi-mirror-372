from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FontScheme (  PptObject) :
    """
    Represents theme-defined fonts for presentation slides.
    """
    @property

    def MinorFont(self)->'LocaleFonts':
        """
        Gets the fonts collection for a "body" part of the slide.
            
        """
        GetDllLibPpt().FontScheme_get_MinorFont.argtypes=[c_void_p]
        GetDllLibPpt().FontScheme_get_MinorFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FontScheme_get_MinorFont,self.Ptr)
        ret = None if intPtr==None else LocaleFonts(intPtr)
        return ret


    @property

    def MajorFont(self)->'LocaleFonts':
        """
        Gets the fonts collection for a "heading" part of the slide.
           
        """
        GetDllLibPpt().FontScheme_get_MajorFont.argtypes=[c_void_p]
        GetDllLibPpt().FontScheme_get_MajorFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FontScheme_get_MajorFont,self.Ptr)
        ret = None if intPtr==None else LocaleFonts(intPtr)
        return ret


    @property

    def Name(self)->str:
        """
        Gets the font scheme name.
        Readonly string.
   
        """
        GetDllLibPpt().FontScheme_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().FontScheme_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().FontScheme_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().FontScheme_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().FontScheme_set_Name,self.Ptr,valuePtr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current object is equal to another object.
        
        Args:
            obj: The object to compare with.
        
        Returns:
            True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FontScheme_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FontScheme_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FontScheme_Equals,self.Ptr, intPtrobj)
        return ret

