from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextFont (SpireObject) :
    """
    Represents an immutable font definition.
    
    Attributes:
        FontName (str): Gets or sets the font name.
    """
    @dispatch
    def __init__(self):
        """
        Initializes a new instance of the TextFont class with default font 'Arail'.
        """
        GetDllLibPpt().Creat_TextFont.argtypes=[c_wchar_p]
        GetDllLibPpt().Creat_TextFont.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Creat_TextFont,'Arail')
        super(TextFont, self).__init__(intPtr)

    @dispatch
    def __init__(self,fontName:str):
        """
        Initializes a new instance of the TextFont class with specified font name.
        
        Args:
            fontName: Name of the font to use.
        """
        fontNamePtr = StrToPtr(fontName)
        GetDllLibPpt().Creat_TextFont.argtypes=[c_char_p]
        GetDllLibPpt().Creat_TextFont.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Creat_TextFont,fontNamePtr)
        super(TextFont, self).__init__(intPtr)
   
    @property

    def FontName(self)->str:
        """
        Gets or sets the font name.
        """
        GetDllLibPpt().TextFont_get_FontName.argtypes=[c_void_p]
        GetDllLibPpt().TextFont_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextFont_get_FontName,self.Ptr))
        return ret


    @FontName.setter
    def FontName(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextFont_set_FontName.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextFont_set_FontName,self.Ptr,valuePtr)


    def GetFontName(self ,theme:'Theme')->str:
        """
        Gets the font name, replacing theme references with actual font names.
        
        Args:
            theme: Theme from which themed font name should be taken.
            
        Returns:
            str: Actual font name used.
        """
        intPtrtheme:c_void_p = theme.Ptr

        GetDllLibPpt().TextFont_GetFontName.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextFont_GetFontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextFont_GetFontName,self.Ptr, intPtrtheme))
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if two TextFont objects are equal.
        
        Args:
            obj: TextFont object to compare.
            
        Returns:
            bool: True if objects are equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextFont_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextFont_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextFont_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
        Gets the hash code for the object.
        
        Returns:
            int: Hash code value.
        """
        GetDllLibPpt().TextFont_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().TextFont_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextFont_GetHashCode,self.Ptr)
        return ret

