from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class TextRange (  TextCharacterProperties) :
    """
    Represents a segment of formatted text within a presentation.
    """

    @dispatch
    def __init__(self):
        """
        Initializes a new empty TextRange instance.
        """
        GetDllLibPpt().TextRange_Create.argtypes=[c_wchar_p]
        GetDllLibPpt().TextRange_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_Create,None)
        super(TextRange, self).__init__(intPtr)

    @dispatch
    def __init__(self,value:str):
        """
        Initializes a new TextRange instance with specified text.

        Args:
            value: The initial text content for the range.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextRange_Create.argtypes=[c_char_p]
        GetDllLibPpt().TextRange_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_Create,valuePtr)
        super(TextRange, self).__init__(intPtr)
    """

    """
    @property

    def Format(self)->'DefaultTextRangeProperties':
        """
        Gets the formatting properties of the text range.

        Returns:
            DefaultTextRangeProperties: Read-only formatting properties.
        """
        GetDllLibPpt().TextRange_get_Format.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_Format.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_get_Format,self.Ptr)
        ret = None if intPtr==None else DefaultTextRangeProperties(intPtr)
        return ret

    @property

    def DisplayFormat(self)->'DefaultTextRangeProperties':
        """
        Gets the display formatting properties of the text range.

        Returns:
            DefaultTextRangeProperties: Read-only display formatting properties.
        """
        GetDllLibPpt().TextRange_get_DisplayFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_DisplayFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_get_DisplayFormat,self.Ptr)
        ret = None if intPtr==None else DefaultTextRangeProperties(intPtr)
        return ret

    @property

    def Paragraph(self)->'TextParagraph':
        """
        Gets the parent paragraph containing this text range.

        Returns:
            TextParagraph: The parent paragraph object.
        """
        from spire.presentation.TextParagraph import TextParagraph
        GetDllLibPpt().TextRange_get_Paragraph.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_Paragraph.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_get_Paragraph,self.Ptr)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret


    @property

    def Text(self)->str:
        """
        Gets or sets the text content of the range.

        Returns:
            str: The current text content.
        """
        GetDllLibPpt().TextRange_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextRange_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextRange_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextRange_set_Text,self.Ptr,valuePtr)

    @property

    def Field(self)->'Field':
        """
        Gets the field associated with this text range (if applicable).

        Returns:
            Field: The associated field object, or None if not a field.
        """
        GetDllLibPpt().TextRange_get_Field.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_Field.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_get_Field,self.Ptr)
        ret = None if intPtr==None else Field(intPtr)
        return ret



    def AddField(self ,fieldType:'FieldType'):
        """
        Converts the text range into a field of specified type.

        Args:
            fieldType: The type of field to create.
        """
        intPtrfieldType:c_void_p = fieldType.Ptr

        GetDllLibPpt().TextRange_AddField.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().TextRange_AddField,self.Ptr, intPtrfieldType)

    def RemoveField(self):
        """
        Removes field formatting from the text range.
        """
        GetDllLibPpt().TextRange_RemoveField.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TextRange_RemoveField,self.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if the current object is equal to another object.

        Args:
            obj: The object to compare with the current object.

        Returns:
            bool: True if the objects are equal; otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextRange_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextRange_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextRange_Equals,self.Ptr, intPtrobj)
        return ret

