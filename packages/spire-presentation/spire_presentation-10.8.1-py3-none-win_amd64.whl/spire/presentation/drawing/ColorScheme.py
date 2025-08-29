from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ColorScheme (  PptObject, IActiveSlide, IActivePresentation) :
    """
    Represents a color scheme with eight colors used for different slide elements.
    """

    def get_Item(self ,index:'ColorSchemeIndex')->'ColorFormat':
        """
        Gets color by index from the scheme.

        Args:
            index (ColorSchemeIndex): Color index in scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        enumindex:c_int = index.value

        GetDllLibPpt().ColorScheme_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ColorScheme_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Item,self.Ptr, enumindex)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if two color schemes are equal.

        Args:
            obj (SpireObject): Scheme to compare.

        Returns:
            bool: True if schemes are equal.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ColorScheme_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ColorScheme_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ColorScheme_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Dark1(self)->'ColorFormat':
        """
        First dark color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Dark1.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Dark1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Dark1,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Light1(self)->'ColorFormat':
        """
        First light color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Light1.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Light1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Light1,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Dark2(self)->'ColorFormat':
        """
        Second dark color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Dark2.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Dark2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Dark2,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Light2(self)->'ColorFormat':
        """
        Second light color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Light2.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Light2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Light2,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Accent1(self)->'ColorFormat':
        """
        First accent color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Accent1.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Accent1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Accent1,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Accent2(self)->'ColorFormat':
        """
        Second accent color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Accent2.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Accent2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Accent2,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Accent3(self)->'ColorFormat':
        """
        Third accent color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Accent3.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Accent3.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Accent3,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Accent4(self)->'ColorFormat':
        """
        Fourth accent color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Accent4.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Accent4.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Accent4,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Accent5(self)->'ColorFormat':
        """
        Fifth accent color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Accent5.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Accent5.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Accent5,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Accent6(self)->'ColorFormat':
        """
        Sixth accent color in the scheme.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_Accent6.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Accent6.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Accent6,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def HyperlinkColor(self)->'ColorFormat':
        """
        Color for hyperlinks.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_HyperlinkColor.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_HyperlinkColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_HyperlinkColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def FollowedHyperlink(self)->'ColorFormat':
        """
        Color for visited hyperlinks.

        Returns:
            ColorFormat: Read-only color format.
        """
        GetDllLibPpt().ColorScheme_get_FollowedHyperlink.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_FollowedHyperlink.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_FollowedHyperlink,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Slide(self)->'ActiveSlide':
        """
        Parent slide of the color scheme.

        Returns:
            ActiveSlide: Read-only slide reference.
        """
        GetDllLibPpt().ColorScheme_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Parent presentation of the color scheme.

        Returns:
            Presentation: Read-only presentation reference.
        """
        GetDllLibPpt().ColorScheme_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ColorScheme_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorScheme_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


