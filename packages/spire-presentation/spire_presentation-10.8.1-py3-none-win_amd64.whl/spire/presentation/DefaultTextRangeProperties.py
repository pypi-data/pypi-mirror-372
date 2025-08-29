from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class DefaultTextRangeProperties (  IActiveSlide) :
    """
    Represents text range formatting properties in a presentation.
    """

    @dispatch
    def __init__(self):
        """
        Initializes a new DefaultTextRangeProperties instance with default formatting.
        """
        GetDllLibPpt().DefaultTextRangeProperties_CreateDefaultTextRangeProperties.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_CreateDefaultTextRangeProperties)
        super(DefaultTextRangeProperties, self).__init__(intPtr)

    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this object equals another SpireObject.
        
        Args:
            obj: The object to compare with
            
        Returns:
            True if objects are equal, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().DefaultTextRangeProperties_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def TextLineFormat(self)->'TextLineFormat':
        """
        Gets text outlining properties.
        
        Returns:
            TextLineFormat: Text outline formatting (read-only)
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_TextLineFormat.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_TextLineFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_TextLineFormat,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets text fill properties.
        
        Returns:
            FillFormat: Text fill formatting (read-only)
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets text effect properties.
        
        Returns:
            EffectDag: Text effect formatting (read-only)
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def HighlightColor(self)->'ColorFormat':
        """
        Gets text highlight color.
        
        Returns:
            ColorFormat: Highlight color (read-only)
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_HighlightColor.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_HighlightColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_HighlightColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def UnderlineFormat(self)->'TextLineFormat':
        """
        Gets underline line formatting.
        
        Returns:
            TextLineFormat: Underline formatting (read-only)
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_UnderlineFormat.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_UnderlineFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_UnderlineFormat,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def UnderlineFill(self)->'FillFormat':
        """
        Gets underline fill properties.
        
        Returns:
            FillFormat: Underline fill (read-only)
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_UnderlineFill.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_UnderlineFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_UnderlineFill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def BookmarkId(self)->str:
        """
        Gets or sets target bookmark identifier.
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_BookmarkId.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_BookmarkId.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_BookmarkId,self.Ptr))
        return ret


    @BookmarkId.setter
    def BookmarkId(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().DefaultTextRangeProperties_set_BookmarkId.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_BookmarkId,self.Ptr,valuePtr)

    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets or sets mouse click hyperlink.
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().DefaultTextRangeProperties_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets or sets mouse hover hyperlink.
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().DefaultTextRangeProperties_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_MouseOver,self.Ptr, value.Ptr)

    @property

    def IsBold(self)->'TriState':
        """
        Gets or sets bold formatting status.
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_IsBold.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_IsBold.restype=c_int
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_IsBold,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsBold.setter
    def IsBold(self, value:'TriState'):
        GetDllLibPpt().DefaultTextRangeProperties_set_IsBold.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_IsBold,self.Ptr, value.value)

    @property

    def IsItalic(self)->'TriState':
        """
        Gets or sets italic formatting status.
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_IsItalic.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_IsItalic.restype=c_int
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_IsItalic,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsItalic.setter
    def IsItalic(self, value:'TriState'):
        GetDllLibPpt().DefaultTextRangeProperties_set_IsItalic.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_IsItalic,self.Ptr, value.value)

    @property

    def Kumimoji(self)->'TriState':
        """
        Indicates whether the numbers should ignore text eastern language-specific vertical text layout.
            
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_Kumimoji.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_Kumimoji.restype=c_int
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_Kumimoji,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @Kumimoji.setter
    def Kumimoji(self, value:'TriState'):
        GetDllLibPpt().DefaultTextRangeProperties_set_Kumimoji.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_Kumimoji,self.Ptr, value.value)

    @property

    def NormaliseHeight(self)->'TriState':
        """
        Indicates whether the height of a text should be normalized.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_NormaliseHeight.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_NormaliseHeight.restype=c_int
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_NormaliseHeight,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @NormaliseHeight.setter
    def NormaliseHeight(self, value:'TriState'):
        GetDllLibPpt().DefaultTextRangeProperties_set_NormaliseHeight.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_NormaliseHeight,self.Ptr, value.value)

    @property

    def NoProofing(self)->'TriState':
        """
        Indicates whether the text would be proofed.
            
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_NoProofing.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_NoProofing.restype=c_int
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_NoProofing,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @NoProofing.setter
    def NoProofing(self, value:'TriState'):
        GetDllLibPpt().DefaultTextRangeProperties_set_NoProofing.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_NoProofing,self.Ptr, value.value)

    @property

    def TextUnderlineType(self)->'TextUnderlineType':
        """
        Gets or sets the text underline type.
            
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_TextUnderlineType.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_TextUnderlineType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_TextUnderlineType,self.Ptr)
        objwraped = TextUnderlineType(ret)
        return objwraped

    @TextUnderlineType.setter
    def TextUnderlineType(self, value:'TextUnderlineType'):
        GetDllLibPpt().DefaultTextRangeProperties_set_TextUnderlineType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_TextUnderlineType,self.Ptr, value.value)

    @property

    def TextCapType(self)->'TextCapType':
        """
        Gets or sets the type of text capitalization.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_TextCapType.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_TextCapType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_TextCapType,self.Ptr)
        objwraped = TextCapType(ret)
        return objwraped

    @TextCapType.setter
    def TextCapType(self, value:'TextCapType'):
        GetDllLibPpt().DefaultTextRangeProperties_set_TextCapType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_TextCapType,self.Ptr, value.value)

    @property

    def TextStrikethroughType(self)->'TextStrikethroughType':
        """
        Gets or sets the strikethrough type of a text.
            
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_TextStrikethroughType.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_TextStrikethroughType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_TextStrikethroughType,self.Ptr)
        objwraped = TextStrikethroughType(ret)
        return objwraped

    @TextStrikethroughType.setter
    def TextStrikethroughType(self, value:'TextStrikethroughType'):
        GetDllLibPpt().DefaultTextRangeProperties_set_TextStrikethroughType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_TextStrikethroughType,self.Ptr, value.value)

    @property
    def SmartTagClean(self)->bool:
        """
        Indicates whether the smart tag should be cleaned.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_SmartTagClean.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_SmartTagClean.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_SmartTagClean,self.Ptr)
        return ret

    @SmartTagClean.setter
    def SmartTagClean(self, value:bool):
        GetDllLibPpt().DefaultTextRangeProperties_set_SmartTagClean.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_SmartTagClean,self.Ptr, value)

    @property
    def FontHeight(self)->float:
        """
        Gets or sets the font height of a text range.
        float.NaN: means height is undefined and should be inherited from the Master.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_FontHeight.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_FontHeight.restype=c_float
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_FontHeight,self.Ptr)
        return ret

    @FontHeight.setter
    def FontHeight(self, value:float):
        GetDllLibPpt().DefaultTextRangeProperties_set_FontHeight.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_FontHeight,self.Ptr, value)

    @property

    def LatinFont(self)->'TextFont':
        """
        Gets or sets the Latin font info.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_LatinFont.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_LatinFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_LatinFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @LatinFont.setter
    def LatinFont(self, value:'TextFont'):
        GetDllLibPpt().DefaultTextRangeProperties_set_LatinFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_LatinFont,self.Ptr, value.Ptr)

    @property

    def EastAsianFont(self)->'TextFont':
        """
        Gets or sets the East Asian font info.
            
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_EastAsianFont.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_EastAsianFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_EastAsianFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @EastAsianFont.setter
    def EastAsianFont(self, value:'TextFont'):
        GetDllLibPpt().DefaultTextRangeProperties_set_EastAsianFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_EastAsianFont,self.Ptr, value.Ptr)

    @property

    def ComplexScriptFont(self)->'TextFont':
        """
        Gets or sets the complex script font info.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_ComplexScriptFont.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_ComplexScriptFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_ComplexScriptFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @ComplexScriptFont.setter
    def ComplexScriptFont(self, value:'TextFont'):
        GetDllLibPpt().DefaultTextRangeProperties_set_ComplexScriptFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_ComplexScriptFont,self.Ptr, value.Ptr)

    @property

    def SymbolFont(self)->'TextFont':
        """
        Gets or sets the symbolic font info.
            
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_SymbolFont.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_SymbolFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_SymbolFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @SymbolFont.setter
    def SymbolFont(self, value:'TextFont'):
        GetDllLibPpt().DefaultTextRangeProperties_set_SymbolFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_SymbolFont,self.Ptr, value.Ptr)

    @property
    def ScriptDistance(self)->float:
        """
        Gets or sets the superscript or subscript text.
            
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_ScriptDistance.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_ScriptDistance.restype=c_float
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_ScriptDistance,self.Ptr)
        return ret

    @ScriptDistance.setter
    def ScriptDistance(self, value:float):
        GetDllLibPpt().DefaultTextRangeProperties_set_ScriptDistance.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_ScriptDistance,self.Ptr, value)

    @property
    def FontMinSize(self)->float:
        """
        Gets or sets the minimal font size.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_FontMinSize.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_FontMinSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_FontMinSize,self.Ptr)
        return ret

    @FontMinSize.setter
    def FontMinSize(self, value:float):
        GetDllLibPpt().DefaultTextRangeProperties_set_FontMinSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_FontMinSize,self.Ptr, value)

    @property

    def Language(self)->str:
        """
        Gets or sets the Id of a language.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_Language.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_Language.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_Language,self.Ptr))
        return ret


    @Language.setter
    def Language(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().DefaultTextRangeProperties_set_Language.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_Language,self.Ptr,valuePtr)

    @property

    def AlternativeLanguage(self)->str:
        """
        Gets or sets the Id of an alternative language.
    
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_AlternativeLanguage.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_AlternativeLanguage.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_AlternativeLanguage,self.Ptr))
        return ret


    @AlternativeLanguage.setter
    def AlternativeLanguage(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().DefaultTextRangeProperties_set_AlternativeLanguage.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_AlternativeLanguage,self.Ptr,valuePtr)

    @property
    def LineSpacing(self)->float:
        """
        Gets or sets the line spacing.
           
        """
        GetDllLibPpt().DefaultTextRangeProperties_get_LineSpacing.argtypes=[c_void_p]
        GetDllLibPpt().DefaultTextRangeProperties_get_LineSpacing.restype=c_float
        ret = CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_get_LineSpacing,self.Ptr)
        return ret

    @LineSpacing.setter
    def LineSpacing(self, value:float):
        GetDllLibPpt().DefaultTextRangeProperties_set_LineSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().DefaultTextRangeProperties_set_LineSpacing,self.Ptr, value)

