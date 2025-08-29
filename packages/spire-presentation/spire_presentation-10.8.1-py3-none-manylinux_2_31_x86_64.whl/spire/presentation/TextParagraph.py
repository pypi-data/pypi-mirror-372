from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
from spire.presentation.ParagraphProperties import ParagraphProperties
from spire.presentation.collections.TextRangeCollection import TextRangeCollection

class TextParagraph (  ParagraphProperties) :
    """
    Represents a paragraph of text within a presentation.
    
    Provides properties and methods to manage paragraph formatting,
    text content, and text ranges within the paragraph.
    """

    @dispatch
    def __init__(self):
        """
        Initializes a new instance of the TextParagraph class with default properties.
        """
        GetDllLibPpt().TextParagraph_Creat.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraph_Creat)
        super(TextParagraph, self).__init__(intPtr)
    
    @property

    def FirstTextRange(self)->'TextRange':
        """
        Gets the first text range in the paragraph.
        
        This property provides access to the initial text range
        within the paragraph for formatting and content manipulation.
        
        Returns:
            TextRange: The first text range object in the paragraph
        """
        GetDllLibPpt().TextParagraph_get_FirstTextRange.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraph_get_FirstTextRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraph_get_FirstTextRange,self.Ptr)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret


    @property

    def TextRanges(self)->'TextRangeCollection':
        """
        Gets the collection of text ranges within the paragraph.
        
        This read-only property provides access to all text ranges
        contained in the paragraph for comprehensive text management.
        
        Returns:
            TextRangeCollection: Collection of text range objects
        """
        GetDllLibPpt().TextParagraph_get_TextRanges.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraph_get_TextRanges.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraph_get_TextRanges,self.Ptr)
        ret = None if intPtr==None else TextRangeCollection(intPtr)
        return ret


    @property

    def ParagraphProperties(self)->'TextParagraphProperties':
        """
        Gets the formatting properties of the paragraph.
        
        This read-only property provides access to the complete set
        of paragraph formatting options including alignment, indentation,
        and spacing settings.
        
        Returns:
            TextParagraphProperties: Formatting properties of the paragraph
        """
        GetDllLibPpt().TextParagraph_get_ParagraphProperties.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraph_get_ParagraphProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraph_get_ParagraphProperties,self.Ptr)
        ret = None if intPtr==None else TextParagraphProperties(intPtr)
        return ret


    @property

    def Text(self)->str:
        """
        Gets or sets the plain text content of the paragraph.
        
        This property allows access to the unformatted text content
        of the entire paragraph, including all text ranges.
        
        Returns:
            str: Current plain text content of the paragraph
        """
        GetDllLibPpt().TextParagraph_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraph_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextParagraph_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """
        Sets the plain text content of the paragraph.
        
        Args:
            value: New plain text content for the paragraph
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextParagraph_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextParagraph_set_Text,self.Ptr,valuePtr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if two TextParagraph objects are equivalent.
        
        Args:
            obj: TextParagraph object to compare with current instance
            
        Returns:
            bool: True if objects are equal, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextParagraph_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextParagraph_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextParagraph_Equals,self.Ptr, intPtrobj)
        return ret

