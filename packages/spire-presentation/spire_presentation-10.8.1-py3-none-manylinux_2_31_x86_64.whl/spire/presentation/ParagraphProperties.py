from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ParagraphProperties (  PptObject, IActiveSlide) :
    """
    Represents formatting properties for paragraphs in presentation text.
    """
    @property

    def Depth(self)->'int':
        """
        Gets or sets the nesting depth of the paragraph.
        
        Higher values indicate deeper nesting in outline structures.
        
        Returns:
            int: Current nesting depth (0-based)
        """
        GetDllLibPpt().ParagraphProperties_get_Depth.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_Depth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_Depth,self.Ptr)
        return ret


    @Depth.setter
    def Depth(self, value:'int'):
        """
        Sets the nesting depth of the paragraph.
        
        Args:
            value (int): New nesting depth value (0-based)
        """
        GetDllLibPpt().ParagraphProperties_set_Depth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_Depth,self.Ptr, value)

    @property

    def BulletType(self)->'TextBulletType':
        """
        Gets or sets the bullet style type for the paragraph.
        
        Returns:
            TextBulletType: Current bullet style enumeration
        """
        GetDllLibPpt().ParagraphProperties_get_BulletType.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletType,self.Ptr)
        objwraped = TextBulletType(ret)
        return objwraped

    @BulletType.setter
    def BulletType(self, value:'TextBulletType'):
        """
        Sets the bullet style type for the paragraph.
        
        Args:
            value (TextBulletType): New bullet style enumeration
        """
        GetDllLibPpt().ParagraphProperties_set_BulletType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletType,self.Ptr, value.value)

    @property
    def BulletChar(self)->int:
        """
        Gets or sets the character used for bullet points.
        
        Returns:
            int: Unicode character code for bullet symbol
        """
        GetDllLibPpt().ParagraphProperties_get_BulletChar.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletChar.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletChar,self.Ptr)
        return ret

    @BulletChar.setter
    def BulletChar(self, value:int):
        """
        Sets the character used for bullet points.
        
        Args:
            value (int): Unicode character code for new bullet symbol
        """
        GetDllLibPpt().ParagraphProperties_set_BulletChar.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletChar,self.Ptr, value)

    @property

    def BulletFont(self)->'TextFont':
        """
        Gets or sets the font used for bullet characters.
        
        Returns:
            TextFont: Current bullet font properties
        """
        GetDllLibPpt().ParagraphProperties_get_BulletFont.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @BulletFont.setter
    def BulletFont(self, value:'TextFont'):
        """
        Sets the font used for bullet characters.
        
        Args:
            value (TextFont): New bullet font properties
        """
        GetDllLibPpt().ParagraphProperties_set_BulletFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletFont,self.Ptr, value.Ptr)

    @property
    def BulletSize(self)->float:
        """
        Gets or sets the size of bullet characters relative to text.
        
        Returns:
            float: Current bullet size as percentage of text size
        """
        GetDllLibPpt().ParagraphProperties_get_BulletSize.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletSize,self.Ptr)
        return ret

    @BulletSize.setter
    def BulletSize(self, value:float):
        """
        Sets the size of bullet characters relative to text.
        
        Args:
            value (float): New bullet size as percentage of text size
        """
        GetDllLibPpt().ParagraphProperties_set_BulletSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletSize,self.Ptr, value)

    @property

    def ParagraphBulletColor(self)->'ColorFormat':
        """
        Gets the color formatting for paragraph bullets.
        
        Read-only property.
        
        Returns:
            ColorFormat: Current bullet color properties
        """
        GetDllLibPpt().ParagraphProperties_get_ParagraphBulletColor.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_ParagraphBulletColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_ParagraphBulletColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def BulletNumber(self)->'int':
        """
        Gets or sets the starting number for numbered lists.
        
        Returns:
            int: Current starting number value
        """
        GetDllLibPpt().ParagraphProperties_get_BulletNumber.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletNumber.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletNumber,self.Ptr)
        return ret


    @BulletNumber.setter
    def BulletNumber(self, value:'int'):
        """
        Sets the starting number for numbered lists.
        
        Args:
            value (int): New starting number value
        """
        GetDllLibPpt().ParagraphProperties_set_BulletNumber.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletNumber,self.Ptr, value)

    @property

    def BulletStyle(self)->'NumberedBulletStyle':
        """
        Gets or sets the numbering style for numbered lists.
        
        Returns:
            NumberedBulletStyle: Current numbering style enumeration
        """
        GetDllLibPpt().ParagraphProperties_get_BulletStyle.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletStyle,self.Ptr)
        objwraped = NumberedBulletStyle(ret)
        return objwraped

    @BulletStyle.setter
    def BulletStyle(self, value:'NumberedBulletStyle'):
        """
        Sets the numbering style for numbered lists.
        
        Args:
            value (NumberedBulletStyle): New numbering style enumeration
        """
        GetDllLibPpt().ParagraphProperties_set_BulletStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletStyle,self.Ptr, value.value)

    @property

    def Alignment(self)->'TextAlignmentType':
        """
        Gets or sets the horizontal alignment of text.
        
        Returns:
            TextAlignmentType: Current text alignment enumeration
        """
        GetDllLibPpt().ParagraphProperties_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_Alignment,self.Ptr)
        objwraped = TextAlignmentType(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'TextAlignmentType'):
        """
        Sets the horizontal alignment of text.
        
        Args:
            value (TextAlignmentType): New text alignment enumeration
        """
        GetDllLibPpt().ParagraphProperties_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_Alignment,self.Ptr, value.value)

    @property
    def LineSpacing(self)->float:
        """
        Gets or sets the spacing between lines of text.
        
        Returns:
            float: Current line spacing value in points
        """
        GetDllLibPpt().ParagraphProperties_get_LineSpacing.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_LineSpacing.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_LineSpacing,self.Ptr)
        return ret

    @LineSpacing.setter
    def LineSpacing(self, value:float):
        """
        Sets the spacing between lines of text.
        
        Args:
            value (float): New line spacing value in points
        """
        GetDllLibPpt().ParagraphProperties_set_LineSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_LineSpacing,self.Ptr, value)

    @property
    def SpaceBefore(self)->float:
        """
        Gets or sets spacing before the paragraph.
        
        Returns:
            float: Current spacing value before paragraph in points
        """
        GetDllLibPpt().ParagraphProperties_get_SpaceBefore.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_SpaceBefore.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_SpaceBefore,self.Ptr)
        return ret

    @SpaceBefore.setter
    def SpaceBefore(self, value:float):
        """
        Sets spacing before the paragraph.
        
        Args:
            value (float): New spacing value before paragraph in points
        """
        GetDllLibPpt().ParagraphProperties_set_SpaceBefore.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_SpaceBefore,self.Ptr, value)

    @property
    def SpaceAfter(self)->float:
        """
        Gets or sets spacing after the paragraph.
        
        Returns:
            float: Current spacing value after paragraph in points
        """
        GetDllLibPpt().ParagraphProperties_get_SpaceAfter.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_SpaceAfter.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_SpaceAfter,self.Ptr)
        return ret

    @SpaceAfter.setter
    def SpaceAfter(self, value:float):
        """
        Sets spacing after the paragraph.
        
        Args:
            value (float): New spacing value after paragraph in points
        """
        GetDllLibPpt().ParagraphProperties_set_SpaceAfter.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_SpaceAfter,self.Ptr, value)

    @property

    def EastAsianLineBreak(self)->'TriState':
        """
        Gets or sets whether to use East Asian line breaking rules.
        
        Returns:
            TriState: Current East Asian line breaking setting
        """
        GetDllLibPpt().ParagraphProperties_get_EastAsianLineBreak.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_EastAsianLineBreak.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_EastAsianLineBreak,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @EastAsianLineBreak.setter
    def EastAsianLineBreak(self, value:'TriState'):
        """
        Sets whether to use East Asian line breaking rules.
        
        Args:
            value (TriState): New East Asian line breaking setting
        """
        GetDllLibPpt().ParagraphProperties_set_EastAsianLineBreak.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_EastAsianLineBreak,self.Ptr, value.value)

    @property

    def RightToLeft(self)->'TriState':
        """
        Gets or sets whether text uses right-to-left reading order.
        
        Returns:
            TriState: Current right-to-left text direction setting
        """
        GetDllLibPpt().ParagraphProperties_get_RightToLeft.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_RightToLeft.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_RightToLeft,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RightToLeft.setter
    def RightToLeft(self, value:'TriState'):
        GetDllLibPpt().ParagraphProperties_set_RightToLeft.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_RightToLeft,self.Ptr, value.value)

    @property

    def LatinLineBreak(self)->'TriState':
        """
        Gets or sets whether to use Latin line breaking rules.
        
        Returns:
            TriState: Current Latin line breaking setting
        """
        GetDllLibPpt().ParagraphProperties_get_LatinLineBreak.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_LatinLineBreak.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_LatinLineBreak,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @LatinLineBreak.setter
    def LatinLineBreak(self, value:'TriState'):
        GetDllLibPpt().ParagraphProperties_set_LatinLineBreak.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_LatinLineBreak,self.Ptr, value.value)

    @property

    def HangingPunctuation(self)->'TriState':
        """
        Gets or sets whether hanging punctuation is enabled.
        
        Hanging punctuation allows punctuation marks to extend beyond text margins.
        
        Returns:
            TriState: Current hanging punctuation setting
        """
        GetDllLibPpt().ParagraphProperties_get_HangingPunctuation.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_HangingPunctuation.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_HangingPunctuation,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @HangingPunctuation.setter
    def HangingPunctuation(self, value:'TriState'):
        GetDllLibPpt().ParagraphProperties_set_HangingPunctuation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_HangingPunctuation,self.Ptr, value.value)

    @property
    def LeftMargin(self)->float:
        """
        Gets or sets the left margin of the paragraph.
        
        Returns:
            float: Current left margin value in points
        """
        GetDllLibPpt().ParagraphProperties_get_LeftMargin.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_LeftMargin.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_LeftMargin,self.Ptr)
        return ret

    @LeftMargin.setter
    def LeftMargin(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_LeftMargin.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_LeftMargin,self.Ptr, value)

    @property
    def RightMargin(self)->float:
        """
        Gets or sets the right margin of the paragraph.
        
        Returns:
            float: Current right margin value in points
        """
        GetDllLibPpt().ParagraphProperties_get_RightMargin.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_RightMargin.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_RightMargin,self.Ptr)
        return ret

    @RightMargin.setter
    def RightMargin(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_RightMargin.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_RightMargin,self.Ptr, value)

    @property
    def Indent(self)->float:
        """
        Gets or sets the text indentation of the paragraph.
        
        Returns:
            float: Current indentation value in points
        """
        GetDllLibPpt().ParagraphProperties_get_Indent.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_Indent.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_Indent,self.Ptr)
        return ret

    @Indent.setter
    def Indent(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_Indent.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_Indent,self.Ptr, value)

    @property
    def DefaultTabSize(self)->float:
        """
        Gets or sets the default tab stop size.
        
        Returns:
            float: Current default tab size in points
        """
        GetDllLibPpt().ParagraphProperties_get_DefaultTabSize.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_DefaultTabSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_DefaultTabSize,self.Ptr)
        return ret

    @DefaultTabSize.setter
    def DefaultTabSize(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_DefaultTabSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_DefaultTabSize,self.Ptr, value)

    @property

    def Tabs(self)->'TabStopCollection':
        """
        Gets the collection of custom tab stops for the paragraph.
        
        Read-only property.
        
        Returns:
            TabStopCollection: Collection of custom tab stops
        """
        GetDllLibPpt().ParagraphProperties_get_Tabs.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_Tabs.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_Tabs,self.Ptr)
        ret = None if intPtr==None else TabStopCollection(intPtr)
        return ret


    @property

    def FontAlignment(self)->'FontAlignmentType':
        """
        Gets or sets the vertical font alignment.
        
        Controls how characters are positioned relative to the text baseline.
        
        Returns:
            FontAlignmentType: Current font alignment enumeration
        """
        GetDllLibPpt().ParagraphProperties_get_FontAlignment.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_FontAlignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_FontAlignment,self.Ptr)
        objwraped = FontAlignmentType(ret)
        return objwraped

    @FontAlignment.setter
    def FontAlignment(self, value:'FontAlignmentType'):
        GetDllLibPpt().ParagraphProperties_set_FontAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_FontAlignment,self.Ptr, value.value)

    @property

    def BulletPicture(self)->'PictureShape':
        """
        Gets the picture used as a custom bullet.
        
        Read-only property.
        
        Returns:
            PictureShape: Picture object used as bullet
        """
        GetDllLibPpt().ParagraphProperties_get_BulletPicture.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletPicture.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletPicture,self.Ptr)
        ret = None if intPtr==None else PictureShape(intPtr)
        return ret


    @property

    def DefaultCharacterProperties(self)->'TextCharacterProperties':
        """
        Gets the default character formatting properties.
        
        Read-only property.
        
        Returns:
            TextCharacterProperties: Default character formatting properties
        """
        GetDllLibPpt().ParagraphProperties_get_DefaultCharacterProperties.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_DefaultCharacterProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_DefaultCharacterProperties,self.Ptr)
        ret = None if intPtr==None else TextCharacterProperties(intPtr)
        return ret


    @property
    def HasBullet(self)->bool:
        """
        Indicates whether the paragraph has a bullet.
        
        Read-only property.
        
        Returns:
            bool: True if paragraph has bullet formatting, False otherwise
        """
        GetDllLibPpt().ParagraphProperties_get_HasBullet.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_HasBullet.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_HasBullet,self.Ptr)
        return ret

    @property
    def CustomBulletColor(self)->bool:
        """
        Indicates whether a custom bullet color is used.
        
        Returns:
            bool: True if custom bullet color is applied, False otherwise
        """
        GetDllLibPpt().ParagraphProperties_get_CustomBulletColor.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_CustomBulletColor.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_CustomBulletColor,self.Ptr)
        return ret

    @CustomBulletColor.setter
    def CustomBulletColor(self, value:bool):
        GetDllLibPpt().ParagraphProperties_set_CustomBulletColor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_CustomBulletColor,self.Ptr, value)

    @property

    def BulletColor(self)->'ColorFormat':
        """
        Gets the color formatting for bullets.
        
        Read-only property.
        
        Returns:
            ColorFormat: Bullet color properties
        """
        GetDllLibPpt().ParagraphProperties_get_BulletColor.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property
    def CustomBulletFont(self)->bool:
        """
        Indicates whether a custom bullet font is used.
        
        Returns:
            bool: True if custom bullet font is applied, False otherwise
        """
        GetDllLibPpt().ParagraphProperties_get_CustomBulletFont.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_CustomBulletFont.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_CustomBulletFont,self.Ptr)
        return ret

    @CustomBulletFont.setter
    def CustomBulletFont(self, value:bool):
        GetDllLibPpt().ParagraphProperties_set_CustomBulletFont.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_CustomBulletFont,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current object is equal to another object.
        
        Args:
            obj: The object to compare with.
        
        Returns:
            True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ParagraphProperties_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphProperties_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_Equals,self.Ptr, intPtrobj)
        return ret

