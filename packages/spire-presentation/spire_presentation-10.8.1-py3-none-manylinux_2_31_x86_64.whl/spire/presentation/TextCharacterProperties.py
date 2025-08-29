from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from spire.presentation.ClickHyperlink import ClickHyperlink
from ctypes import *
from spire.presentation.TextFont import TextFont

class TextCharacterProperties (  IActiveSlide) :
    """
    Represents a text range with formatting.

    This class provides access to various text formatting properties such as font, color, underline,
    hyperlinks, and other character-level formatting attributes.
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current object is equal to another object.

        Args:
            obj: The object to compare with the current object.

        Returns:
            bool: True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextCharacterProperties_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextCharacterProperties_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Format(self)->'DefaultTextRangeProperties':
        """
        Gets the text range format for this object (read-only).

        Returns:
            DefaultTextRangeProperties: The formatting properties of the text range.
        """
        GetDllLibPpt().TextCharacterProperties_get_Format.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_Format.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_Format,self.Ptr)
        ret = None if intPtr==None else DefaultTextRangeProperties(intPtr)
        return ret


    @property

    def TextLineFormat(self)->'TextLineFormat':
        """
        Gets the LineFormat properties for text outlining (read-only).

        Returns:
            TextLineFormat: The line formatting properties for text outlines.
        """
        GetDllLibPpt().TextCharacterProperties_get_TextLineFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_TextLineFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_TextLineFormat,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets the text FillFormat properties (read-only).

        Returns:
            FillFormat: The fill formatting properties for the text.
        """
        GetDllLibPpt().TextCharacterProperties_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def DisplayFill(self)->'FillFormat':
        """
        Gets the effective fill properties including inherited values (read-only).

        If textRange FillType is Undefined, displays fill properties inherited from paragraph/textFrame/layoutSlide/master.

        Returns:
            FillFormat: The effective fill formatting properties.
        """
        GetDllLibPpt().TextCharacterProperties_get_DisplayFill.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_DisplayFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_DisplayFill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets the text EffectFormat properties (read-only).

        Returns:
            EffectDag: The special effect properties for the text.
        """
        GetDllLibPpt().TextCharacterProperties_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def HighlightColor(self)->'ColorFormat':
        """
        Gets the color used to highlight text (read-only).

        Returns:
            ColorFormat: The highlight color properties.
        """
        GetDllLibPpt().TextCharacterProperties_get_HighlightColor.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_HighlightColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_HighlightColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def UnderlineFormat(self)->'TextLineFormat':
        """
        Gets the LineFormat properties for underline (read-only).

        Returns:
            TextLineFormat: The underline line formatting properties.
        """
        GetDllLibPpt().TextCharacterProperties_get_UnderlineFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_UnderlineFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_UnderlineFormat,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def UnderlineFillFormat(self)->'FillFormat':
        """
        Gets the fill properties for underline lines (read-only).

        Returns:
            FillFormat: The fill formatting properties for underlines.
        """
        GetDllLibPpt().TextCharacterProperties_get_UnderlineFillFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_UnderlineFillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_UnderlineFillFormat,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def BookmarkId(self)->str:
        """
        Gets or sets the bookmark identifier (read/write).

        Returns:
            str: The unique identifier for the bookmark.
        """
        GetDllLibPpt().TextCharacterProperties_get_BookmarkId.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_BookmarkId.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextCharacterProperties_get_BookmarkId,self.Ptr))
        return ret


    @BookmarkId.setter
    def BookmarkId(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextCharacterProperties_set_BookmarkId.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_BookmarkId,self.Ptr,valuePtr)

    @property
    def HasClickAction(self)->bool:
        """
        Indicates whether text has a hyperlink action (read-only).

        Returns:
            bool: True if text has a click action; otherwise False.
        """
        GetDllLibPpt().TextCharacterProperties_get_HasClickAction.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_HasClickAction.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_HasClickAction,self.Ptr)
        return ret

    @property

    def ClickAction(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink for mouse click (read/write).

        Returns:
            ClickHyperlink: The hyperlink action configuration.
        """
        GetDllLibPpt().TextCharacterProperties_get_ClickAction.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_ClickAction.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_ClickAction,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @ClickAction.setter
    def ClickAction(self, value:'ClickHyperlink'):
        GetDllLibPpt().TextCharacterProperties_set_ClickAction.argtypes=[c_void_p, c_void_p]
        if(value == None):
            CallCFunction(GetDllLibPpt().TextCharacterProperties_set_ClickAction,self.Ptr, None)
        else:
            CallCFunction(GetDllLibPpt().TextCharacterProperties_set_ClickAction,self.Ptr, value.Ptr)

    @property

    def MouseOverAction(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink for mouse hover (read/write).

        Returns:
            ClickHyperlink: The mouseover hyperlink configuration.
        """
        GetDllLibPpt().TextCharacterProperties_get_MouseOverAction.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_MouseOverAction.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_MouseOverAction,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOverAction.setter
    def MouseOverAction(self, value:'ClickHyperlink'):
        GetDllLibPpt().TextCharacterProperties_set_MouseOverAction.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_MouseOverAction,self.Ptr, value.Ptr)

    @property

    def IsBold(self)->'TriState':
        """
        Gets or sets whether the font is bold (read/write).

        Returns:
            TriState: The bold formatting state (True, False, or Inherit).
        """
        GetDllLibPpt().TextCharacterProperties_get_IsBold.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_IsBold.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_IsBold,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsBold.setter
    def IsBold(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_IsBold.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_IsBold,self.Ptr, value.value)

    @property

    def IsItalic(self)->'TriState':
        """
        Gets or sets whether the font is italic (read/write).

        Returns:
            TriState: The italic formatting state.
        """
        GetDllLibPpt().TextCharacterProperties_get_IsItalic.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_IsItalic.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_IsItalic,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsItalic.setter
    def IsItalic(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_IsItalic.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_IsItalic,self.Ptr, value.value)

    @property

    def Kumimoji(self)->'TriState':
        """
        Gets or sets whether to use East-Asian vertical text layout (read/write).

        Returns:
            TriState: The vertical text layout state.
        """
        GetDllLibPpt().TextCharacterProperties_get_Kumimoji.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_Kumimoji.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_Kumimoji,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @Kumimoji.setter
    def Kumimoji(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_Kumimoji.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_Kumimoji,self.Ptr, value.value)

    @property

    def NormalizeHeights(self)->'TriState':
        """
        Gets or sets whether to normalize text height (read/write).

        Returns:
            TriState: The text height normalization state.
        """
        GetDllLibPpt().TextCharacterProperties_get_NormalizeHeights.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_NormalizeHeights.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_NormalizeHeights,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @NormalizeHeights.setter
    def NormalizeHeights(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_NormalizeHeights.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_NormalizeHeights,self.Ptr, value.value)

    @property

    def NoProofing(self)->'TriState':
        """
        Gets or sets whether text should be spell-checked (read/write).

        Returns:
            TriState: The proofing state.
        """
        GetDllLibPpt().TextCharacterProperties_get_NoProofing.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_NoProofing.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_NoProofing,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @NoProofing.setter
    def NoProofing(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_NoProofing.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_NoProofing,self.Ptr, value.value)

    @property

    def TextUnderlineType(self)->'TextUnderlineType':
        """
        Gets or sets the underline style (read/write).

        Returns:
            TextUnderlineType: The type of underline (None, Single, Double, etc.).
        """
        GetDllLibPpt().TextCharacterProperties_get_TextUnderlineType.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_TextUnderlineType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_TextUnderlineType,self.Ptr)
        objwraped = TextUnderlineType(ret)
        return objwraped

    @TextUnderlineType.setter
    def TextUnderlineType(self, value:'TextUnderlineType'):
        GetDllLibPpt().TextCharacterProperties_set_TextUnderlineType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_TextUnderlineType,self.Ptr, value.value)

    @property

    def TextCapType(self)->'TextCapType':
        """
        Gets or sets the capitalization style (read/write).

        Returns:
            TextCapType: The capitalization type (None, Small, All, etc.).
        """
        GetDllLibPpt().TextCharacterProperties_get_TextCapType.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_TextCapType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_TextCapType,self.Ptr)
        objwraped = TextCapType(ret)
        return objwraped

    @TextCapType.setter
    def TextCapType(self, value:'TextCapType'):
        GetDllLibPpt().TextCharacterProperties_set_TextCapType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_TextCapType,self.Ptr, value.value)

    @property

    def TextStrikethroughType(self)->'TextStrikethroughType':
        """
        Gets or sets the strikethrough style (read/write).

        Returns:
            TextStrikethroughType: The strikethrough type (None, Single, Double).
        """
        GetDllLibPpt().TextCharacterProperties_get_TextStrikethroughType.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_TextStrikethroughType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_TextStrikethroughType,self.Ptr)
        objwraped = TextStrikethroughType(ret)
        return objwraped

    @TextStrikethroughType.setter
    def TextStrikethroughType(self, value:'TextStrikethroughType'):
        GetDllLibPpt().TextCharacterProperties_set_TextStrikethroughType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_TextStrikethroughType,self.Ptr, value.value)

    @property
    def SmartTagClean(self)->bool:
        """
        Gets or sets whether smart tags should be cleaned (read/write).

        Returns:
            bool: True to clean smart tags; otherwise False.
        """
        GetDllLibPpt().TextCharacterProperties_get_SmartTagClean.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_SmartTagClean.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_SmartTagClean,self.Ptr)
        return ret

    @SmartTagClean.setter
    def SmartTagClean(self, value:bool):
        GetDllLibPpt().TextCharacterProperties_set_SmartTagClean.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_SmartTagClean,self.Ptr, value)

    @property

    def IsInheritUnderlineFill(self)->'TriState':
        """
        Gets or sets whether underline fill is inherited (read/write).

        Returns:
            TriState: The underline fill inheritance state.
        """
        GetDllLibPpt().TextCharacterProperties_get_IsInheritUnderlineFill.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_IsInheritUnderlineFill.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_IsInheritUnderlineFill,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsInheritUnderlineFill.setter
    def IsInheritUnderlineFill(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_IsInheritUnderlineFill.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_IsInheritUnderlineFill,self.Ptr, value.value)

    @property
    def FontHeight(self)->float:
        """
        Gets or sets the font size in points (read/write).

        Returns:
            float: The font height in points.
        """
        GetDllLibPpt().TextCharacterProperties_get_FontHeight.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_FontHeight.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_FontHeight,self.Ptr)
        return ret

    @FontHeight.setter
    def FontHeight(self, value:float):
        GetDllLibPpt().TextCharacterProperties_set_FontHeight.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_FontHeight,self.Ptr, value)

    @property

    def LatinFont(self)->'TextFont':
        """
        Gets or sets the Latin (Western) font (read/write).

        Returns:
            TextFont: The Latin font properties.
        """
        GetDllLibPpt().TextCharacterProperties_get_LatinFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_LatinFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_LatinFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @LatinFont.setter
    def LatinFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_LatinFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_LatinFont,self.Ptr, value.Ptr)

    @property

    def DefaultLatinFont(self)->'TextFont':
        """
        Gets or sets the default Latin font (read/write).

        Returns:
            TextFont: The default Latin font properties.
        """
        GetDllLibPpt().TextCharacterProperties_get_DefaultLatinFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_DefaultLatinFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_DefaultLatinFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @DefaultLatinFont.setter
    def DefaultLatinFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_DefaultLatinFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_DefaultLatinFont,self.Ptr, value.Ptr)

    @property

    def EastAsianFont(self)->'TextFont':
        """
        Gets or sets the East Asian font (read/write).

        Returns:
            TextFont: The East Asian font properties.
        """
        GetDllLibPpt().TextCharacterProperties_get_EastAsianFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_EastAsianFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_EastAsianFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @EastAsianFont.setter
    def EastAsianFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_EastAsianFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_EastAsianFont,self.Ptr, value.Ptr)

    @property

    def ComplexScriptFont(self)->'TextFont':
        """
        Gets or sets the complex script font (read/write).

        Returns:
            TextFont: The complex script font properties.
        """
        GetDllLibPpt().TextCharacterProperties_get_ComplexScriptFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_ComplexScriptFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_ComplexScriptFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @ComplexScriptFont.setter
    def ComplexScriptFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_ComplexScriptFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_ComplexScriptFont,self.Ptr, value.Ptr)

    @property

    def SymbolFont(self)->'TextFont':
        """
        Gets or sets the symbolic font (read/write).

        Returns:
            TextFont: The symbolic font properties.
        """
        GetDllLibPpt().TextCharacterProperties_get_SymbolFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_SymbolFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_SymbolFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @SymbolFont.setter
    def SymbolFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_SymbolFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_SymbolFont,self.Ptr, value.Ptr)

    @property
    def ScriptDistance(self)->float:
        """
        Gets or sets superscript/subscript offset (read/write).

        Positive values = superscript, Negative values = subscript.

        Returns:
            float: The script offset value.
        """
        GetDllLibPpt().TextCharacterProperties_get_ScriptDistance.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_ScriptDistance.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_ScriptDistance,self.Ptr)
        return ret

    @ScriptDistance.setter
    def ScriptDistance(self, value:float):
        GetDllLibPpt().TextCharacterProperties_set_ScriptDistance.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_ScriptDistance,self.Ptr, value)

    @property
    def FontMinSize(self)->float:
        """
        Gets or sets the minimum font size (read/write).

        Returns:
            float: The minimum allowed font size in points.
        """
        GetDllLibPpt().TextCharacterProperties_get_FontMinSize.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_FontMinSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_FontMinSize,self.Ptr)
        return ret

    @FontMinSize.setter
    def FontMinSize(self, value:float):
        GetDllLibPpt().TextCharacterProperties_set_FontMinSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_FontMinSize,self.Ptr, value)

    @property

    def Language(self)->str:
        """
        Gets or sets the primary language (read/write).

        Returns:
            str: The language identifier (e.g., "en-US").
        """
        GetDllLibPpt().TextCharacterProperties_get_Language.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_Language.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextCharacterProperties_get_Language,self.Ptr))
        return ret


    @Language.setter
    def Language(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextCharacterProperties_set_Language.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_Language,self.Ptr,valuePtr)

    @property

    def AlternativeLanguage(self)->str:
        """
        Gets or sets the alternative language (read/write).

        Returns:
            str: The alternative language identifier.
        """
        GetDllLibPpt().TextCharacterProperties_get_AlternativeLanguage.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_AlternativeLanguage.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextCharacterProperties_get_AlternativeLanguage,self.Ptr))
        return ret


    @AlternativeLanguage.setter
    def AlternativeLanguage(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextCharacterProperties_set_AlternativeLanguage.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_AlternativeLanguage,self.Ptr,valuePtr)

    @property
    def LineSpacing(self)->float:
        """
        Gets or sets the line spacing (read/write).

        Returns:
            float: The line spacing value.
        """
        GetDllLibPpt().TextCharacterProperties_get_LineSpacing.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_LineSpacing.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_LineSpacing,self.Ptr)
        return ret

    @LineSpacing.setter
    def LineSpacing(self, value:float):
        GetDllLibPpt().TextCharacterProperties_set_LineSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_LineSpacing,self.Ptr, value)

