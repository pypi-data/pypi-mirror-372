from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ITextFrameProperties (SpireObject) :
    """
    Represents text formatting and layout properties for text containers.
    
    Provides comprehensive control over text presentation including 
    paragraphs, styles, margins, alignment, and special effects.
    """
    @property

    def Paragraphs(self)->'ParagraphCollection':
        """
        Gets the collection of paragraphs in the text frame.
        
        Returns:
            ParagraphCollection: Collection of paragraph objects.
        """
        GetDllLibPpt().ITextFrameProperties_get_Paragraphs.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Paragraphs.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Paragraphs,self.Ptr)
        ret = None if intPtr==None else ParagraphCollection(intPtr)
        return ret


    @property

    def Text(self)->str:
        """
        Gets or sets the plain text content of the text frame.
        
        Returns:
            str: Current text content.
        """

        GetDllLibPpt().ITextFrameProperties_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Text.restype=c_void_p
        ret =PtrToStr(CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        """
        Sets plain text content.
        
        Args:
            value (str): New text content.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ITextFrameProperties_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_Text,self.Ptr,valuePtr)

    @property

    def TextStyle(self)->'TextStyle':
        """
        Gets the default text style for the text frame.
        
        Returns:
            TextStyle: Object containing text style definitions.
        """
        GetDllLibPpt().ITextFrameProperties_get_TextStyle.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_TextStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_TextStyle,self.Ptr)
        ret = None if intPtr==None else TextStyle(intPtr)
        return ret


    @property
    def MarginLeft(self)->float:
        """
        Gets or sets the left margin (in points).
        
        Returns:
            float: Current left margin value.
        """
        GetDllLibPpt().ITextFrameProperties_get_MarginLeft.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_MarginLeft.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_MarginLeft,self.Ptr)
        return ret

    @MarginLeft.setter
    def MarginLeft(self, value:float):
        """
        Sets left margin.
        
        Args:
            value (float): New left margin in points.
        """
        GetDllLibPpt().ITextFrameProperties_set_MarginLeft.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_MarginLeft,self.Ptr, value)

    @property
    def ColumnCount(self)->int:
        """
        Gets or sets number of text columns.
        
        Returns:
            int: Current column count.
        """
        GetDllLibPpt().ITextFrameProperties_get_ColumnCount.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_ColumnCount.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_ColumnCount,self.Ptr)
        return ret

    @ColumnCount.setter
    def ColumnCount(self, value:int):
        """
        Sets number of text columns.
        
        Args:
            value (int): New column count.
        """
        GetDllLibPpt().ITextFrameProperties_set_ColumnCount.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_ColumnCount,self.Ptr, value)

    @property
    def ColumnSpacing(self)->float:
        """
        Gets or sets spacing between text columns.
        
        Returns:
            float: Current column spacing.
        """
        GetDllLibPpt().ITextFrameProperties_get_ColumnSpacing.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_ColumnSpacing.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_ColumnSpacing,self.Ptr)
        return ret

    @ColumnSpacing.setter
    def ColumnSpacing(self, value:float):
        """
        Sets spacing between columns.
        
        Args:
            value (float): New column spacing value.
        """
        GetDllLibPpt().ITextFrameProperties_set_ColumnSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_ColumnSpacing,self.Ptr, value)

    @property
    def MarginRight(self)->float:
        """
        Gets or sets the right margin (in points).
        
        Returns:
            float: Current right margin value.
        """
        GetDllLibPpt().ITextFrameProperties_get_MarginRight.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_MarginRight.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_MarginRight,self.Ptr)
        return ret

    @MarginRight.setter
    def MarginRight(self, value:float):
        """
        Sets right margin.
        
        Args:
            value (float): New right margin in points.
        """
        GetDllLibPpt().ITextFrameProperties_set_MarginRight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_MarginRight,self.Ptr, value)

    @property
    def MarginTop(self)->float:
        """
        Gets or sets the top margin (in points).
        
        Returns:
            float: Current top margin value.
        """
        GetDllLibPpt().ITextFrameProperties_get_MarginTop.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_MarginTop.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_MarginTop,self.Ptr)
        return ret

    @MarginTop.setter
    def MarginTop(self, value:float):
        """
        Sets top margin.
        
        Args:
            value (float): New top margin in points.
        """
        GetDllLibPpt().ITextFrameProperties_set_MarginTop.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_MarginTop,self.Ptr, value)

    @property
    def MarginBottom(self)->float:
        """
        Gets or sets the bottom margin (in points).
        
        Returns:
            float: Current bottom margin value.
        """
        GetDllLibPpt().ITextFrameProperties_get_MarginBottom.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_MarginBottom.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_MarginBottom,self.Ptr)
        return ret

    @MarginBottom.setter
    def MarginBottom(self, value:float):
        """
        Sets bottom margin.
        
        Args:
            value (float): New bottom margin in points.
        """
        GetDllLibPpt().ITextFrameProperties_set_MarginBottom.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_MarginBottom,self.Ptr, value)

    @property

    def TextRange(self)->'TextRange':
        """
        Gets the text range with formatting properties.
        
        Returns:
            TextRange: Object containing formatted text.
        """
        GetDllLibPpt().ITextFrameProperties_get_TextRange.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_TextRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_TextRange,self.Ptr)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret


    @property
    def WordWrap(self)->bool:
        """
        Controls whether text wraps at container margins.
        
        Returns:
            bool: True if word wrap is enabled, False otherwise.
        """
        GetDllLibPpt().ITextFrameProperties_get_WordWrap.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_WordWrap.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_WordWrap,self.Ptr)
        return ret

    @WordWrap.setter
    def WordWrap(self, value:bool):
        """
        Enables/disables word wrapping.
        
        Args:
            value (bool): True to enable wrapping, False to disable.
        """
        GetDllLibPpt().ITextFrameProperties_set_WordWrap.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_WordWrap,self.Ptr, value)

    @property

    def AnchoringType(self)->'TextAnchorType':
        """
        Gets or sets vertical text anchoring.
        
        Returns:
            TextAnchorType: Current vertical anchoring type.
        """
        GetDllLibPpt().ITextFrameProperties_get_AnchoringType.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_AnchoringType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_AnchoringType,self.Ptr)
        objwraped = TextAnchorType(ret)
        return objwraped

    @AnchoringType.setter
    def AnchoringType(self, value:'TextAnchorType'):
        """
        Sets vertical anchoring type.
        
        Args:
            value (TextAnchorType): New anchoring type enum value.
        """
        GetDllLibPpt().ITextFrameProperties_set_AnchoringType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_AnchoringType,self.Ptr, value.value)

    @property
    def IsCentered(self)->bool:
        """
        Controls horizontal centering of text.
        
        Returns:
            bool: True if text is horizontally centered.
        """
        GetDllLibPpt().ITextFrameProperties_get_IsCentered.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_IsCentered.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_IsCentered,self.Ptr)
        return ret

    @IsCentered.setter
    def IsCentered(self, value:bool):
        """
        Enables/disables horizontal centering.
        
        Args:
            value (bool): True to center text horizontally.
        """
        GetDllLibPpt().ITextFrameProperties_set_IsCentered.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_IsCentered,self.Ptr, value)

    @property

    def VerticalTextType(self)->'VerticalTextType':
        """
        Gets or sets text orientation direction.
        
        Returns:
            VerticalTextType: Current text orientation type.
        """

        GetDllLibPpt().ITextFrameProperties_get_VerticalTextType.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_VerticalTextType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_VerticalTextType,self.Ptr)
        objwraped = VerticalTextType(ret)
        return objwraped

    @VerticalTextType.setter
    def VerticalTextType(self, value:'VerticalTextType'):
        """
        Sets text orientation direction.
        
        Args:
            value (VerticalTextType): New orientation type enum value.
        """
        GetDllLibPpt().ITextFrameProperties_set_VerticalTextType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_VerticalTextType,self.Ptr, value.value)

    @property

    def AutofitType(self)->'TextAutofitType':
        """
        Gets or sets text autofitting behavior.
        
        Returns:
            TextAutofitType: Current autofit type.
        """
        GetDllLibPpt().ITextFrameProperties_get_AutofitType.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_AutofitType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_AutofitType,self.Ptr)
        objwraped = TextAutofitType(ret)
        return objwraped

    @AutofitType.setter
    def AutofitType(self, value:'TextAutofitType'):
        """
        Sets autofitting behavior.
        
        Args:
            value (TextAutofitType): New autofit type enum value.
        """
        GetDllLibPpt().ITextFrameProperties_set_AutofitType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_AutofitType,self.Ptr, value.value)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide of the text frame.
        
        Returns:
            ActiveSlide: Parent slide object.
        """
        GetDllLibPpt().ITextFrameProperties_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation.
        
        Returns:
            Presentation: Parent presentation object.
        """
        GetDllLibPpt().ITextFrameProperties_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
        Gets the parent object.
        
        Returns:
            SpireObject: Parent object reference.
        """
        GetDllLibPpt().ITextFrameProperties_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def Dispose(self):
        """
        Releases resources associated with the text frame.
        """
        GetDllLibPpt().ITextFrameProperties_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_Dispose,self.Ptr)

    @property

    def TextThreeD(self)->'FormatThreeD':
        """
        Gets 3D text effect properties.
        
        Returns:
            FormatThreeD: Object containing 3D effect settings.
        """
        GetDllLibPpt().ITextFrameProperties_get_TextThreeD.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_TextThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_TextThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property
    def RotationAngle(self)->float:
        """
        Gets or sets text rotation angle.
        
        Returns:
            float: Current rotation angle in degrees.
        """
        GetDllLibPpt().ITextFrameProperties_get_RotationAngle.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_RotationAngle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_RotationAngle,self.Ptr)
        return ret

    @RotationAngle.setter
    def RotationAngle(self, value:float):
        """
        Sets text rotation angle.
        
        Args:
            value (float): New rotation angle in degrees.
        """
        GetDllLibPpt().ITextFrameProperties_set_RotationAngle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_RotationAngle,self.Ptr, value)


    def HighLightText(self ,text:str,color:'Color',options:'TextHighLightingOptions'):
        """
        Highlights all occurrences of specified text.
        
        Args:
            text (str): Text to highlight
            color (Color): Highlight color
            options (TextHighLightingOptions): Highlighting options
        """
        intPtrcolor:c_void_p = color.Ptr
        intPtroptions:c_void_p = options.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().ITextFrameProperties_HighLightText.argtypes=[c_void_p ,c_char_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_HighLightText,self.Ptr,textPtr,intPtrcolor,intPtroptions)

    @property
    def RightToLeftColumns(self)->bool:
        """
        Controls right-to-left column direction.
        
        Returns:
            bool: True if columns use right-to-left flow.
        """
        GetDllLibPpt().ITextFrameProperties_get_RightToLeftColumns.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_RightToLeftColumns.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_RightToLeftColumns,self.Ptr)
        return ret

    @RightToLeftColumns.setter
    def RightToLeftColumns(self, value:bool):
        """
        Sets column flow direction.
        
        Args:
            value (bool): True for right-to-left column flow.
        """
        GetDllLibPpt().ITextFrameProperties_set_RightToLeftColumns.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_RightToLeftColumns,self.Ptr, value)

    @property

    def TextShapeType(self)->'TextShapeType':
        """
        Gets or sets text container shape type.
        
        Returns:
            TextShapeType: Current text container shape type.
        """
        GetDllLibPpt().ITextFrameProperties_get_TextShapeType.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_TextShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_TextShapeType,self.Ptr)
        objwraped = TextShapeType(ret)
        return objwraped

    @TextShapeType.setter
    def TextShapeType(self, value:'TextShapeType'):
        """
        Sets text container shape type.
        
        Args:
            value (TextShapeType): New shape type enum value.
        """
        GetDllLibPpt().ITextFrameProperties_set_TextShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_TextShapeType,self.Ptr, value.value)


    def GetLayoutLines(self)->List['LineText']:
        """
        Gets laid out text lines information.
        
        Returns:
            List[LineText]: Collection of line text objects.
        """
        GetDllLibPpt().ITextFrameProperties_GetLayoutLines.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_GetLayoutLines.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ITextFrameProperties_GetLayoutLines,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, LineText)
        return ret
    

    def GetTextLocation(self)->PointF:
        """
        Gets the position of the text frame.
        
        Returns:
            PointF: (x, y) coordinates of text position.
        """
        GetDllLibPpt().ITextFrameProperties_GetTextLocation.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_GetTextLocation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_GetTextLocation,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret
    

    def GetTextSize(self)->SizeF:
        """
        Gets dimensions of the text frame.
        
        Returns:
            SizeF: (width, height) dimensions of text area.
        """
        GetDllLibPpt().ITextFrameProperties_GetTextSize.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_GetTextSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_GetTextSize,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret

