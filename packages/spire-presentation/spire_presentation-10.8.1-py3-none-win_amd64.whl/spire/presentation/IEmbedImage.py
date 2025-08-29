from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IEmbedImage (  IShape) :
    """
    Represents an embedded image shape within a slide.
    """
    @property

    def ShapeLocking(self)->'SlidePictureLocking':
        """
        Gets the shape's locking settings.
        
        Returns:
            SlidePictureLocking: Read-only picture locking properties.
        """
        GetDllLibPpt().IEmbedImage_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else SlidePictureLocking(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """
        Type of the shape (get/set).
        """
        GetDllLibPpt().IEmbedImage_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        """
        Sets the type of the shape.
        
        Args:
            value (ShapeType): New shape type.
        """
        GetDllLibPpt().IEmbedImage_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_ShapeType,self.Ptr, value.value)

    @property

    def PictureFill(self)->'PictureFillFormat':
        """
        Picture fill formatting properties.
        """
        GetDllLibPpt().IEmbedImage_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    @property

    def ShapeStyle(self)->'ShapeStyle':
        """Gets shape style properties."""
        GetDllLibPpt().IEmbedImage_get_ShapeStyle.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_ShapeStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_ShapeStyle,self.Ptr)
        ret = None if intPtr==None else ShapeStyle(intPtr)
        return ret


    @property

    def Adjustments(self)->'ShapeAdjustCollection':
        """Gets shape adjustment values collection."""
        GetDllLibPpt().IEmbedImage_get_Adjustments.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Adjustments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Adjustments,self.Ptr)
        ret = None if intPtr==None else ShapeAdjustCollection(intPtr)
        return ret


    @property
    def IsPlaceholder(self)->bool:
        """
        Indicates whether the shape is a placeholder.
        
        Returns:
            bool: True if placeholder, False otherwise.
        """
        GetDllLibPpt().IEmbedImage_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_IsPlaceholder,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
        Gets placeholder properties.
        
        Returns:
            Placeholder: Read-only placeholder object.
        """
        GetDllLibPpt().IEmbedImage_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the shape's tags collection.
        
        Returns:
            TagCollection: Read-only tag collection.
        """
        GetDllLibPpt().IEmbedImage_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
        Gets or sets frame properties.
        
        Returns:
            GraphicFrame: Frame properties object.
        """
        GetDllLibPpt().IEmbedImage_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        """
        Sets frame properties.
        
        Args:
            value (GraphicFrame): New frame properties.
        """
        GetDllLibPpt().IEmbedImage_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets line formatting properties.
        
        Returns:
            TextLineFormat: Line format object (may be null).
        """
        GetDllLibPpt().IEmbedImage_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
        Gets 3D effect properties.
        
        Returns:
            FormatThreeD: 3D format object (may be null).
        """
        GetDllLibPpt().IEmbedImage_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets pixel effects applied to shape.
        
        Returns:
            EffectDag: Effect object (may be null).
        """
        GetDllLibPpt().IEmbedImage_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets fill formatting properties.
        
        Returns:
            FillFormat: Fill format object (may be null).
        """
        GetDllLibPpt().IEmbedImage_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
        Sets mouse click hyperlink.
        
        Args:
            value (ClickHyperlink): New click hyperlink.
        """
        GetDllLibPpt().IEmbedImage_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().IEmbedImage_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
        Gets or sets mouse over hyperlink.
        
        Returns:
            ClickHyperlink: Hyperlink for mouseover action.
        """
        GetDllLibPpt().IEmbedImage_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        """
        Sets mouse over hyperlink.
        
        Args:
            value (ClickHyperlink): New mouseover hyperlink.
        """
        GetDllLibPpt().IEmbedImage_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
        Indicates whether shape is hidden.
        
        Returns:
            bool: True if hidden, False otherwise.
        """
        GetDllLibPpt().IEmbedImage_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        """
        Sets shape visibility.
        
        Args:
            value (bool): True to hide, False to show.
        """
        GetDllLibPpt().IEmbedImage_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
        Gets parent slide.
        
        Returns:
            ActiveSlide: Read-only parent slide.
        """
        GetDllLibPpt().IEmbedImage_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
        Gets or sets z-order position.
        
        Returns:
            int: Z-order position index.
        """
        GetDllLibPpt().IEmbedImage_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        """
        Sets z-order position.
        
        Args:
            value (int): New z-order position.
        """
        GetDllLibPpt().IEmbedImage_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
        Gets or sets rotation angle.
        
        Returns:
            float: Rotation in degrees (positive = clockwise).
        """
        GetDllLibPpt().IEmbedImage_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        """
        Sets rotation angle.
        
        Args:
            value (float): New rotation in degrees.
        """
        GetDllLibPpt().IEmbedImage_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
        Gets or sets horizontal position.
        
        Returns:
            float: X-coordinate of upper-left corner.
        """
        GetDllLibPpt().IEmbedImage_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        """
        Sets horizontal position.
        
        Args:
            value (float): New left position.
        """
        GetDllLibPpt().IEmbedImage_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
        Gets or sets vertical position.
        
        Returns:
            float: Y-coordinate of upper-left corner.
        """
        GetDllLibPpt().IEmbedImage_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        """
        Sets vertical position.
        
        Args:
            value (float): New top position.
        """
        GetDllLibPpt().IEmbedImage_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
        Gets or sets shape width.
        
        Returns:
            float: Width of the shape.
        """
        GetDllLibPpt().IEmbedImage_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        """
        Sets shape width.
        
        Args:
            value (float): New width value.
        """
        GetDllLibPpt().IEmbedImage_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets shape height.
        
        Returns:
            float: Height of the shape.
        """
        GetDllLibPpt().IEmbedImage_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IEmbedImage_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        """
        Sets shape height.
        
        Args:
            value (float): New height value.
        """
        GetDllLibPpt().IEmbedImage_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
        Gets or sets alternative text.
        
        Returns:
            str: Alternative text description.
        """
        GetDllLibPpt().IEmbedImage_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IEmbedImage_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        """
        Sets alternative text.
        
        Args:
            value (str): New alternative text.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IEmbedImage_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
        Gets or sets shape name.
        
        Returns:
            str: Name of the shape.
        """
        GetDllLibPpt().IEmbedImage_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IEmbedImage_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets shape name.
        
        Args:
            value (str): New shape name.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IEmbedImage_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IEmbedImage_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets parent slide.
        
        Returns:
            ActiveSlide: Read-only parent slide.
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IEmbedImage_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """Gets parent presentation object."""
        GetDllLibPpt().IEmbedImage_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IEmbedImage_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IEmbedImage_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    def RemovePlaceholder(self):
        """Removes placeholder properties from the shape."""
        GetDllLibPpt().IEmbedImage_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IEmbedImage_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """Releases resources associated with the object."""
        GetDllLibPpt().IEmbedImage_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IEmbedImage_Dispose,self.Ptr)

