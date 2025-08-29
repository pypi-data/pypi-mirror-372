from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LocaleFonts (SpireObject) :
    """
    Represents a collection of fonts for different language locales.
    
    This class manages font settings for different character sets used in multilingual documents.
    """
    @property

    def LatinFont(self)->'TextFont':
        """
        Gets or sets the font used for Latin characters.
        
        Returns:
            TextFont: The font used for Latin character set.
        """
        GetDllLibPpt().LocaleFonts_get_LatinFont.argtypes=[c_void_p]
        GetDllLibPpt().LocaleFonts_get_LatinFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LocaleFonts_get_LatinFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @LatinFont.setter
    def LatinFont(self, value:'TextFont'):
        """
        Sets the font used for Latin characters.
        
        Args:
            value (TextFont): The font to use for Latin character set.
        """
        GetDllLibPpt().LocaleFonts_set_LatinFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().LocaleFonts_set_LatinFont,self.Ptr, value.Ptr)

    @property

    def EastAsianFont(self)->'TextFont':
        """
        Gets or sets the font used for East Asian characters.
        
        Returns:
            TextFont: The font used for East Asian character set.
        """
        GetDllLibPpt().LocaleFonts_get_EastAsianFont.argtypes=[c_void_p]
        GetDllLibPpt().LocaleFonts_get_EastAsianFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LocaleFonts_get_EastAsianFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @EastAsianFont.setter
    def EastAsianFont(self, value:'TextFont'):
        """
        Sets the font used for East Asian characters.
        
        Args:
            value (TextFont): The font to use for East Asian character set.
        """
        GetDllLibPpt().LocaleFonts_set_EastAsianFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().LocaleFonts_set_EastAsianFont,self.Ptr, value.Ptr)

    @property

    def ComplexScriptFont(self)->'TextFont':
        """
        Gets or sets the font used for complex script characters.
        
        Returns:
            TextFont: The font used for complex script character set.
        """
        GetDllLibPpt().LocaleFonts_get_ComplexScriptFont.argtypes=[c_void_p]
        GetDllLibPpt().LocaleFonts_get_ComplexScriptFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LocaleFonts_get_ComplexScriptFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @ComplexScriptFont.setter
    def ComplexScriptFont(self, value:'TextFont'):
        """
        Sets the font used for complex script characters.
        
        Args:
            value (TextFont): The font to use for complex script character set.
        """
        GetDllLibPpt().LocaleFonts_set_ComplexScriptFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().LocaleFonts_set_ComplexScriptFont,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current LocaleFonts object.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LocaleFonts_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LocaleFonts_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LocaleFonts_Equals,self.Ptr, intPtrobj)
        return ret

