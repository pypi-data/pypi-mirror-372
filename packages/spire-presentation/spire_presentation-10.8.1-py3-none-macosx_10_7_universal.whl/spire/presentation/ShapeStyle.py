from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeStyle (  IActiveSlide, IActivePresentation) :
    """
    Represents a shape's style reference.

    Provides access to color formatting, style indexes, and presentation context
    for various visual aspects of a shape (line, fill, effects, font).
    """
    @property

    def LineColor(self)->'ColorFormat':
        """
        Gets the outline color of the shape.

        Returns:
            ColorFormat: Read-only color format object for the shape's outline.
        """
        GetDllLibPpt().ShapeStyle_get_LineColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_LineColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_LineColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def LineStyleIndex(self)->'UInt16':
        """
        Gets or sets the line style index in the style matrix.

        Returns:
            UInt16: Column index of the line style in theme matrices.
        """
        GetDllLibPpt().ShapeStyle_get_LineStyleIndex.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_LineStyleIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_LineStyleIndex,self.Ptr)
        ret = None if intPtr==None else UInt16(intPtr)
        return ret


    @LineStyleIndex.setter
    def LineStyleIndex(self, value:'UInt16'):
        """
        Sets the line style index in the style matrix.

        Args:
            value (UInt16): New column index for line style.
        """
        GetDllLibPpt().ShapeStyle_set_LineStyleIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeStyle_set_LineStyleIndex,self.Ptr, value.Ptr)

    @property

    def FillColor(self)->'ColorFormat':
        """
        Gets the fill color of the shape.

        Returns:
            ColorFormat: Read-only color format object for the shape's fill.
        """
        GetDllLibPpt().ShapeStyle_get_FillColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_FillColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_FillColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def FillStyleIndex(self)->'Int16':
        """
        Gets or sets the fill style index in style matrices.

        Returns:
            Int16: 
            0 = No fill
            Positive = Index in theme's fill styles
            Negative = Index in theme's background styles
        """
        GetDllLibPpt().ShapeStyle_get_FillStyleIndex.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_FillStyleIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_FillStyleIndex,self.Ptr)
        ret = None if intPtr==None else Int16(intPtr)
        return ret


    @FillStyleIndex.setter
    def FillStyleIndex(self, value:'Int16'):
        GetDllLibPpt().ShapeStyle_set_FillStyleIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeStyle_set_FillStyleIndex,self.Ptr, value.Ptr)

    @property

    def EffectColor(self)->'ColorFormat':
        """
        Gets the effect color of the shape.

        Returns:
            ColorFormat: Read-only color format object for shape effects.
        """
        GetDllLibPpt().ShapeStyle_get_EffectColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_EffectColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_EffectColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def EffectStyleIndex(self)->'UInt32':
        """
        Gets or sets the effect style index in the style matrix.

        Returns:
            UInt32: Column index of the effect style in theme matrices.
        """
        GetDllLibPpt().ShapeStyle_get_EffectStyleIndex.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_EffectStyleIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_EffectStyleIndex,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret


    @EffectStyleIndex.setter
    def EffectStyleIndex(self, value:'UInt32'):
        GetDllLibPpt().ShapeStyle_set_EffectStyleIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeStyle_set_EffectStyleIndex,self.Ptr, value.Ptr)

    @property

    def FontColor(self)->'ColorFormat':
        """
        Gets the font color of the shape.

        Returns:
            ColorFormat: Read-only color format object for text.
        """
        GetDllLibPpt().ShapeStyle_get_FontColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_FontColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_FontColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def FontCollectionIndex(self)->'FontCollectionIndex':
        """
        Gets or sets the font index in the font collection.

        Returns:
            FontCollectionIndex: Index value in the presentation's font collection.
        """
        GetDllLibPpt().ShapeStyle_get_FontCollectionIndex.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_FontCollectionIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeStyle_get_FontCollectionIndex,self.Ptr)
        objwraped = FontCollectionIndex(ret)
        return objwraped

    @FontCollectionIndex.setter
    def FontCollectionIndex(self, value:'FontCollectionIndex'):
        GetDllLibPpt().ShapeStyle_set_FontCollectionIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeStyle_set_FontCollectionIndex,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this style is equal to another object.

        Args:
            obj (SpireObject): The object to compare with.

        Returns:
            bool: True if objects are equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShapeStyle_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeStyle_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeStyle_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide of the shape style.

        Returns:
            ActiveSlide: Read-only reference to the parent slide.
        """
        GetDllLibPpt().ShapeStyle_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation of the shape style.

        Returns:
            Presentation: Read-only reference to the parent presentation.
        """
        GetDllLibPpt().ShapeStyle_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


