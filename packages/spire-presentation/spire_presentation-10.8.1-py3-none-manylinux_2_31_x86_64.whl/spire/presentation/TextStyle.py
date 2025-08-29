from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextStyle (  IActiveSlide, IActivePresentation) :
    """
    Represents text styling properties for presentation elements.
    
    This class provides access to different levels of text formatting styles.
    """

    def GetListLevelTextStyle(self ,index:int)->'TextParagraphProperties':
        """Retrieves paragraph properties for a specific list level if exists.
        
        Args:
            index: Zero-based index of the text level (0-8 for PowerPoint)
            
        Returns:
            TextParagraphProperties for the specified level if exists, 
            otherwise None.
        """
        
        GetDllLibPpt().TextStyle_GetListLevelTextStyle.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextStyle_GetListLevelTextStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextStyle_GetListLevelTextStyle,self.Ptr, index)
        ret = None if intPtr==None else TextParagraphProperties(intPtr)
        return ret



    def GetOrCreateListLevelTextStyle(self ,index:int)->'TextParagraphProperties':
        """
        Retrieves or creates paragraph properties for a specific list level.
        
        Args:
            index: Zero-based index of the text level (0-8 for PowerPoint)
            
        Returns:
            Existing or newly created TextParagraphProperties for the level.
        """
        
        GetDllLibPpt().TextStyle_GetOrCreateListLevelTextStyle.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextStyle_GetOrCreateListLevelTextStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextStyle_GetOrCreateListLevelTextStyle,self.Ptr, index)
        ret = None if intPtr==None else TextParagraphProperties(intPtr)
        return ret


    @property

    def DefaultParagraphStyle(self)->'TextParagraphProperties':
        """
        Provides access to default paragraph formatting properties.
        
        Returns:
            TextParagraphProperties object containing default formatting.
        """
        GetDllLibPpt().TextStyle_get_DefaultParagraphStyle.argtypes=[c_void_p]
        GetDllLibPpt().TextStyle_get_DefaultParagraphStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextStyle_get_DefaultParagraphStyle,self.Ptr)
        ret = None if intPtr==None else TextParagraphProperties(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """Determines whether this style equals another object.
        
        Args:
            obj: The SpireObject to compare with
            
        Returns:
            True if objects are equivalent, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextStyle_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextStyle_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextStyle_Equals,self.Ptr, intPtrobj)
        return ret

